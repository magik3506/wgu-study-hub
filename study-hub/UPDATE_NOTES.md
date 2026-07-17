# Study Hub update — music that survives, a chattier mascot, launchers

**How to apply:** unzip `wgu-study-hub-update.zip` **over your existing
`study-hub/` folder**, letting it replace files. Nothing outside the zip is
touched — your `courses/`, your voice `.wav`s, your icons, and your progress
in `~/.wgu_study_hub` all stay exactly as they are. Then start the hub as
usual (or with the new launchers below).

*Optional tidy-up:* you can delete `core/webdist/assets/` **before**
unzipping — it only holds old built bundles, and the zip brings a fresh set.
Skipping this is harmless; the old files just sit unused.

---

## 1 · Music no longer resets between pages (the mute bug)

**Root cause:** every link in the app (`home → course`, the logo, "Back to
the hub") was a full page load. That tears down the whole document — hidden
YouTube player included — so each hop built a *new* player, and browsers only
allow autoplay **muted**. Your unmute never stood a chance.

**Fix:** the app now routes client-side (`web/src/App.jsx`). Internal
navigation intercepts the click, `pushState`s, and re-renders — the document
never reloads, so the player, the current track, its position, and your mute
choice all survive the trip. Back/forward buttons work; downloads (the study
guide PDF), new-tab clicks, and modifier-key clicks keep native behavior.

A genuinely fresh launch still starts muted — that's the browser's autoplay
policy, not the hub. One click on the note icon and it stays unmuted for the
whole session. If YouTube can't load (offline), the controls now dim with a
"Music offline" label instead of silently doing nothing.

## 2 · Event voice lines

The mascot now reacts (`web/src/sound.js` owns all of it):

| Event                | When it plays                                        |
|----------------------|------------------------------------------------------|
| `answered_correctly` | a drill / SQL-drill answer graded correct            |
| `answered_incorrectly`| graded wrong — **skips count as wrong**, matching mastery stats |
| `scoring_well`       | drill finished with score **> 85 %** (replaces the last right/wrong line) |
| `scoring_bad`        | drill finished with score **< 65 %** (same)          |
| `general_advice`     | after **10 quiet minutes** (no lines played), repeating every 10 min while idle |
| `too_long`           | session **> 3 h**, then every 30 min — with a "take a break" banner over the top bar |

Files are read straight from your repo's `assets/voicelines/<type>/`
folders — **any file names, any count, `.wav` / `.mp3` / `.ogg` / `.m4a`
all work**. The server scans the folders (`/api/voicelines`) and serves
them read-only (`/media/`), and the mascot picks randomly from whatever is
actually there — your `answered_correctly_01.wav … _05.wav` files work
as-is. Dropping in new or replacement files needs no rebuild, no renaming,
no restart of anything but the hub. Missing files fail silently. Music
auto-ducks to ~20 % while any line plays, then restores. One line plays at
a time; a new one interrupts the old.

The 10 classic click lines (with their on-screen text) still work on both
portraits and now run through the same channel, so they duck the music too.
They stay exactly where they are — `web/public/static/voice/` in source,
`core/webdist/static/voice/` built, served at `/static/voice/` — **nothing
to move**; only the six *event* folders live under `assets/voicelines/`.

*Tweaks, each one line in `web/src/sound.js`:* thresholds and timings are the
constants at the top (`SCORE_BAD_BELOW`, `ADVICE_IDLE_MS`, …). To make
**skips silent** instead of "wrong", add `if (d.skipped && !d.summary) return;`
at the top of `reportAnswer`. (Changing `web/src/*` needs `npm run build` —
see README.)

## 3 · UI polish

- **Hero speech bubble** rebuilt: it floats beside the portrait (appearing no
  longer shifts the page), pops in, and its tail is drawn from the theme's
  own panel/border variables — so it finally matches in **both** dark and
  light mode (the old arrow was hardcoded slate `#1e293b`).
- **Course-page mascot** is now a tidy dock: portrait **150 px** (was 240 —
  one constant, `PORTRAIT_SIZE` in `web/src/pages/Course.jsx`, puts it back),
  gold ring, gentle float, glow + speech bubble while talking, and a **✕ to
  collapse** it to a small round button so it never covers a drill.
- **Pomodoro** got a progress bar and a Focus/Break color-coded label.
- **Music controls**: real SVG previous/next icons (goodbye text glyphs),
  clearer Now-playing/Muted/Offline states.
- **Break banner** (the 3-hour nudge): amber strip over the top bar,
  dismissible, auto-hides after 30 s.

## 4 · Launchers & installer — no npm, ever, for users

- **`Start Study Hub.bat`** (Windows), **`Start Study Hub.command`** (macOS),
  **`start-study-hub.sh`** (Linux): double-click → the hub opens. They find
  Python themselves and print friendly install directions if it's missing.
- **`install.py`** (optional, stdlib-only): creates a desktop shortcut on any
  OS. `python3 install.py` once and you're done.
- The web UI ships **pre-built** in `core/webdist/` (this zip includes a
  fresh build with everything above). Node/npm is only ever needed to *edit*
  the UI source under `web/`.

## 5 · Stopping the hub — no terminal, no `ps aux`

Double-clicking `start-study-hub.sh` in some Linux file managers runs it
with **no visible window**, which used to leave killing the PID as the only
way out. Three fixes:

- **⏻ power button** in the app's top bar (top right): confirms, shuts the
  server down cleanly, and shows a "hub stopped — you can close this tab"
  screen. This is the everyday way.
- **Stop launchers**: `Stop Study Hub.bat` / `Stop Study Hub.command` /
  `stop-study-hub.sh` — double-click, done.
- **`python3 wgu_study_hub.py --stop`**: finds a running hub (it checks the
  default port and the ones the hub scans to when busy), verifies it really
  is the hub before touching it, and asks it to shut down.

Under the hood it's a loopback-only `POST /api/shutdown` in
`core/webapp.py`. Ctrl+C still works when the hub runs in a terminal, and
the `install.py` desktop shortcut opens a terminal (`Terminal=true`), so
that path always had a window.

## Files in this update

    wgu_study_hub.py                   new --stop flag
    core/webapp.py                     /media route, /api/voicelines,
                                       /api/shutdown, audio MIMEs (v3.1)
    core/webdist/                      freshly built UI (your voice .wavs and
                                       icons in there are left untouched)
    web/src/sound.js                   NEW — music + voice + timers
    web/src/App.jsx                    client-side routing
    web/src/ui.jsx                     controls, bubble, banner, power button
    web/src/index.css                  bubble/float/eq/banner styles
    web/src/pages/Home.jsx             polished hero bubble
    web/src/pages/Course.jsx           mascot dock + pomodoro polish
    web/src/features/Drill.jsx         voice hook on answers
    web/src/features/SqlDrill.jsx      voice hook on answers
    web/public/static/hero-portrait.png
    web/vite.config.js, web/package.json
    Start Study Hub.bat / .command / start-study-hub.sh
    Stop Study Hub.bat / .command / stop-study-hub.sh
    install.py, assets/voicelines/README.txt
    README.md, UPDATE_NOTES.md
