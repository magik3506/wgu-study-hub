/* Sound system — one module owns everything that makes noise.
 *
 *   Music   — a single hidden YouTube playlist player, created once per page
 *             LOAD (not per React render). With client-side routing (App.jsx)
 *             the document never reloads while you move between the homepage
 *             and courses, so the track, position, and mute state all carry
 *             over. A fresh launch still starts muted — browsers only allow
 *             muted autoplay until you've interacted.
 *   Voice   — the mascot. One shared audio channel (new lines interrupt old),
 *             music auto-ducks while the owl talks. Click lines have on-screen
 *             text; event lines are audio files (.wav/.mp3/…) you drop into
 *             assets/voicelines/<type>/ under ANY names — the server lists
 *             what's on disk (/api/voicelines) and serves it (/media/), so
 *             adding or renaming lines never needs a rebuild.
 *   Events  — answered right/wrong, drill scored well/badly, "you've gone
 *             quiet" advice every 10 idle minutes, and a 3-hour "take a
 *             break" nudge (with a banner) repeating every 30 minutes.
 *
 * Tune the behavior here: */
const PLAYLIST_ID = "PLt7bG0K25iXj2h1eql20RZIPB_2CtK659";
const DUCK_VOLUME = 22;                       // music % while the owl speaks
const ADVICE_IDLE_MS = 10 * 60 * 1000;        // silence before general_advice
const TOO_LONG_AFTER_MS = 3 * 60 * 60 * 1000; // session length before too_long
const TOO_LONG_REPEAT_MS = 30 * 60 * 1000;    // ...and how often it repeats
const BANNER_AUTOHIDE_MS = 30 * 1000;         // break banner lifetime
const SCORE_BAD_BELOW = 65;                   // drill % thresholds
const SCORE_WELL_ABOVE = 85;

/** The events the app emits. What actually plays for each comes from the
 *  server's /api/voicelines manifest — whatever audio files exist in
 *  assets/voicelines/<type>/ (any names, any count). */
export const VOICE_EVENT_TYPES = [
  "answered_correctly",
  "answered_incorrectly",
  "general_advice",
  "scoring_bad",
  "scoring_well",
  "too_long",
];

let voiceManifest = null; // {type: [urls]} once loaded; null while fetching
const FALLBACK_LINES = 5; // only for the pre-manifest / old-server fallback

/** Click lines (portrait pokes) — these ship inside webdist/static/voice. */
export const CLICK_LINES = [
  { text: "Boop! Systems online and ready to assist.", src: "/static/voice/01_systems_online.wav" },
  { text: "Hoo's ready to write some code?", src: "/static/voice/02_whos_ready.wav" },
  { text: "Hello, World! What are we studying next?", src: "/static/voice/03_hello_world.wav" },
  { text: "Did you just poke my UI? I felt that!", src: "/static/voice/04_poke_ui.wav" },
  { text: "My algorithms predict a highly productive session today.", src: "/static/voice/05_algorithms.wav" },
  { text: "Night owl mode activated. Let's get to work!", src: "/static/voice/06_night_owl.wav" },
  { text: "At your service! Let's pull up the next module.", src: "/static/voice/07_at_your_service.wav" },
  { text: "Let's compile some knowledge and crush those objectives!", src: "/static/voice/08_compile_knowledge.wav" },
  { text: "Ready to catch some bugs and ace some practice tests?", src: "/static/voice/09_catch_bugs.wav" },
  { text: "I'm fully charged and my syntax is flawless. How about you?", src: "/static/voice/10_fully_charged.wav" },
];

/* ---------------------------------------------------------------- utils -- */

const listeners = new Set();
function notify() {
  listeners.forEach((fn) => {
    try { fn(); } catch { /* a broken subscriber never kills the bus */ }
  });
}
/** Subscribe to any sound-state change (music + voice + banner). */
export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function ssGet(key, fallback) {
  try {
    const v = sessionStorage.getItem(key);
    return v === null ? fallback : Number(v);
  } catch {
    return fallback;
  }
}
function ssSet(key, val) {
  try { sessionStorage.setItem(key, String(val)); } catch { /* private mode */ }
}

/* ---------------------------------------------------------------- music -- */

let ytPlayer = null;
let ytReady = false;
let ytFailed = false;      // offline / blocked — controls render disabled
let muted = true;
let title = "Lofi Study Beats";
let volumeBeforeDuck = null;

function updateTitle(player) {
  try {
    const data = player.getVideoData();
    if (data && data.title) {
      title = data.title;
      notify();
    }
  } catch { /* ignore */ }
}

function ensureYT() {
  return new Promise((resolve) => {
    if (window.YT && window.YT.Player) {
      resolve();
      return;
    }
    if (!window._ytLoading) {
      window._ytLoading = true;
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      tag.onerror = () => {
        ytFailed = true;
        notify();
      };
      document.head.appendChild(tag);
    }
    const prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (prev) prev();
      resolve();
    };
  });
}

function createPlayer() {
  if (ytPlayer || typeof window === "undefined" || !window.YT) return;
  const container = document.createElement("div");
  container.style.cssText = "position:absolute;left:-9999px;width:0;height:0;";
  document.body.appendChild(container);
  try {
    ytPlayer = new window.YT.Player(container, {
      height: "0",
      width: "0",
      playerVars: {
        listType: "playlist",
        list: PLAYLIST_ID,
        autoplay: 1,
        mute: 1,
        controls: 0,
        disablekb: 1,
        fs: 0,
        modestbranding: 1,
        playsinline: 1,
        rel: 0,
      },
      events: {
        onReady: (e) => {
          e.target.playVideo();
          e.target.mute();
          ytReady = true;
          ytFailed = false;
          updateTitle(e.target);
          notify();
        },
        onStateChange: (e) => {
          if (e.data === window.YT.PlayerState.PLAYING) updateTitle(e.target);
        },
      },
    });
  } catch {
    ytFailed = true;
    notify();
  }
}

if (typeof window !== "undefined") {
  ensureYT().then(createPlayer);
  // If the API never shows up (offline / blocked), stop pretending.
  setTimeout(() => {
    if (!ytReady && !ytPlayer) {
      ytFailed = true;
      notify();
    }
  }, 8000);
  // Learn which voice-line files actually exist (names, counts, formats).
  fetch("/api/voicelines")
    .then((r) => (r.ok ? r.json() : {}))
    .then((m) => { voiceManifest = m && typeof m === "object" ? m : {}; })
    .catch(() => { voiceManifest = {}; });
}

export function musicState() {
  return {
    ready: ytReady,
    unavailable: ytFailed && !ytReady,
    muted,
    title: ytFailed && !ytReady ? "Music offline" : title,
  };
}

export function toggleMute() {
  if (!ytPlayer || !ytReady) return;
  if (muted) {
    ytPlayer.unMute();
    muted = false;
  } else {
    ytPlayer.mute();
    muted = true;
  }
  notify();
}

export function prevTrack() {
  if (ytPlayer && ytReady) ytPlayer.previousVideo();
}

export function nextTrack() {
  if (ytPlayer && ytReady) ytPlayer.nextVideo();
}

function duckMusic() {
  if (!ytPlayer || !ytReady || muted) return;
  try {
    if (volumeBeforeDuck === null) volumeBeforeDuck = ytPlayer.getVolume();
    ytPlayer.setVolume(Math.min(DUCK_VOLUME, volumeBeforeDuck));
  } catch { /* ignore */ }
}

function unduckMusic() {
  if (volumeBeforeDuck === null) return;
  try {
    if (ytPlayer && ytReady) ytPlayer.setVolume(volumeBeforeDuck);
  } catch { /* ignore */ }
  volumeBeforeDuck = null;
}

/* ---------------------------------------------------------------- voice -- */

let voiceAudio = null;           // the single shared channel
let voiceNow = null;             // { kind, text } while speaking, else null
const lastPick = {};             // type -> last index, to avoid repeats

const now = () => Date.now();
const sessionStart = ssGet("hub-session-start", now());
ssSet("hub-session-start", sessionStart);
let lastTrigger = ssGet("hub-voice-last-trigger", now());
let lastTooLong = ssGet("hub-voice-last-toolong", 0);

export function voiceState() {
  return voiceNow;
}

function markTrigger() {
  lastTrigger = now();
  ssSet("hub-voice-last-trigger", lastTrigger);
}

function stopVoice() {
  if (voiceAudio) {
    try { voiceAudio.pause(); } catch { /* ignore */ }
    voiceAudio = null;
  }
  if (voiceNow) {
    voiceNow = null;
    notify();
  }
  unduckMusic();
}

function playSrc(src, { kind, text }) {
  stopVoice();
  markTrigger();
  voiceNow = { kind, text: text || null };
  notify();

  let audio;
  try {
    audio = new Audio(src);
  } catch {
    stopVoice();
    return;
  }
  voiceAudio = audio;
  duckMusic();

  const done = () => {
    if (voiceAudio === audio) stopVoice();
  };
  audio.onended = done;
  audio.onerror = done;             // missing file → just go quiet
  try {
    const p = audio.play();
    if (p && typeof p.catch === "function") p.catch(done);
  } catch {
    done();
  }
}

function pickIndex(type, count) {
  let i = Math.floor(Math.random() * count);
  if (count > 1 && i === lastPick[type]) {
    i = (i + 1) % count; // nudge off an immediate repeat
  }
  lastPick[type] = i;
  return i;
}

/** Play a random line for an event type (see VOICE_EVENT_TYPES) — chosen
 *  from the files the server actually found on disk. */
export function speakEvent(type) {
  const list = voiceManifest && voiceManifest[type];
  if (list && list.length) {
    playSrc(list[pickIndex(type, list.length)], { kind: type });
    return;
  }
  if (!VOICE_EVENT_TYPES.includes(type)) return;
  // Manifest not available (loading, or an older server): try the standard
  // layout directly — assets/voicelines/<type>/<type>_01.wav … _05.wav.
  const n = 1 + pickIndex(type, FALLBACK_LINES);
  playSrc(`/media/voicelines/${type}/${type}_0${n}.wav`, { kind: type });
}

/** Play a random portrait-click line; its text is shown in the bubble. */
export function speakClickLine() {
  const line = CLICK_LINES[Math.floor(Math.random() * CLICK_LINES.length)];
  playSrc(line.src, { kind: "click", text: line.text });
}

/** Silence everything — used when the hub is being shut down, so the music
 *  doesn't keep playing over the "hub stopped" screen. */
export function stopAllSound() {
  stopVoice();
  if (ytPlayer && ytReady && !muted) {
    try { ytPlayer.mute(); } catch { /* ignore */ }
    muted = true;
    notify();
  }
}

/** Drill/SQL-drill hook — call with the /api/quiz/answer response.
 *  On the final answer the score line wins (outside the 65–85 band);
 *  otherwise the per-answer line plays. Skips count as incorrect, same as
 *  the mastery stats do. */
export function reportAnswer(d) {
  if (d.summary) {
    const pct = d.summary.pct;
    if (pct < SCORE_BAD_BELOW) return speakEvent("scoring_bad");
    if (pct > SCORE_WELL_ABOVE) return speakEvent("scoring_well");
  }
  speakEvent(d.correct ? "answered_correctly" : "answered_incorrectly");
}

/* --------------------------------------------------------- break banner -- */

let bannerShownAt = 0;

export function bannerState() {
  return {
    visible: bannerShownAt > 0 && now() - bannerShownAt < BANNER_AUTOHIDE_MS,
    shownAt: bannerShownAt,
    sessionHours: (now() - sessionStart) / 3.6e6,
  };
}

export function dismissBanner() {
  bannerShownAt = 0;
  notify();
}

/* --------------------------------------------------------------- timers -- */

if (typeof window !== "undefined") {
  setInterval(() => {
    const t = now();

    // 3h+ session: too_long line + banner, then every 30 min.
    if (t - sessionStart >= TOO_LONG_AFTER_MS &&
        t - lastTooLong >= TOO_LONG_REPEAT_MS) {
      lastTooLong = t;
      ssSet("hub-voice-last-toolong", lastTooLong);
      bannerShownAt = t;
      speakEvent("too_long");            // also resets the idle timer
      setTimeout(notify, BANNER_AUTOHIDE_MS + 500); // let the banner clear
      return;
    }

    // 10 quiet minutes: a bit of general advice (repeats while idle).
    if (t - lastTrigger >= ADVICE_IDLE_MS) {
      speakEvent("general_advice");
    }
  }, 15 * 1000);
}
