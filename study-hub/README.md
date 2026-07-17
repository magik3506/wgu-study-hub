# WGU Study Hub

A local, zero-install study environment for WGU courses: adaptive exam
drills weighted like the real OA, a MySQL-flavored SQL playground (for SQL
courses), hands-on SQL tasks graded by execution, a mastery map, and each
course's study guide — all in one place, all offline.

**Requirements:** Python 3.8+ standard library. Nothing to pip install.
The web UI ships pre-built (React, dark/light theme, night-owl by
default) — running the hub needs no Node, npm, or network.

## Run it

Easiest — double-click the launcher for your OS (it finds Python for you,
and tells you exactly what to install if it's missing):

    Start Study Hub.bat          Windows
    Start Study Hub.command      macOS
    start-study-hub.sh           Linux

Optional: `python3 install.py` once puts a **WGU Study Hub** shortcut on
your desktop.

**Stopping it:** click the **⏻ power button** in the app's top bar (top
right) — no terminal needed. Or double-click `Stop Study Hub.bat` /
`Stop Study Hub.command` / `stop-study-hub.sh`, or run
`python3 wgu_study_hub.py --stop`. If you started it *from* a terminal,
Ctrl+C there works too. (Heads-up: double-clicking `start-study-hub.sh` in
some Linux file managers runs it with no visible window — the power button
is how you stop it then. The `install.py` desktop shortcut always opens a
terminal.)

Or from a terminal:

    python3 wgu_study_hub.py                    # web app (opens browser)
    python3 wgu_study_hub.py --stop             # stop a running hub
    python3 wgu_study_hub.py --cli d426         # terminal REPL + drills
    python3 wgu_study_hub.py --cli d426 --quiz 10
    python3 wgu_study_hub.py --cli d426 --sql 5
    python3 wgu_study_hub.py --selftest         # validate every course pack
    python3 wgu_study_hub.py --list             # show discovered courses

## Layout

    wgu_study_hub.py      the only file you run
    Start Study Hub.*     double-click launchers (Windows / macOS / Linux)
    install.py            optional desktop-shortcut setup
    core/                 engine, grader, harness, server — course-agnostic
    core/webdist/         the built web UI (ships with the framework)
    web/                  frontend source (React + Vite + Tailwind) —
                          only needed if you're changing the UI itself
    assets/voicelines/    the mascot's event voice lines (.mp3) — see below
    courses/<slug>/       one folder per class = one card on the homepage
        course.py         manifest (code, name, blueprint, topics)
        content.py        concepts, sample databases, question generators
        study_guide.pdf   shown in the course's Study guide tab (optional)
    courses/_template/    copy this to start a new course
    skills/               the Claude skills that build packs (upload to your
                          Claude project so future sessions can run them)

Suggested home: keep this folder at `~/wgu/study-hub/`, and raw course
materials (chapter PDFs, practice tests) at `~/wgu/sources/<course>/` —
sources are only needed once, at pack-build time.

The hub and courses ship separately: `wgu-study-hub.zip` is the framework
(replace it wholesale on updates — your course folders and progress are
untouched); each course arrives as `<slug>-pack.zip`, which unzips into
`courses/`. Installing a class is one unzip; updating the framework never
carries your content with it.

## Music & the mascot

The top bar plays a lofi study playlist (hidden YouTube player) with
previous / next / mute controls. Navigation is client-side, so the track
and your mute choice survive moving between the homepage and courses — a
fresh launch starts muted because browsers only allow muted autoplay; one
click un-mutes for the whole session. Offline? The controls dim and the hub
carries on without music.

The owl talks. Click either portrait for one of the classic lines, and it
reacts on its own to how the studying is going:

    answered_correctly / answered_incorrectly   every graded drill answer
    scoring_well  /  scoring_bad                drill finished >85% / <65%
    general_advice                              10 quiet minutes, repeating
    too_long                                    3-hour sessions — voice plus
                                                a "take a break" banner

Each event picks randomly among the audio files in its folder:

    assets/voicelines/<type>/       any names, any count — .wav, .mp3,
                                    .ogg, .m4a all fine (e.g. scoring_well/
                                    scoring_well_03.wav)

The server lists what's actually on disk (`/api/voicelines`) and serves it
read-only at `/media/…` — **drop in new or replacement files and they're
live on the next hub start, no build, no code, no renaming**. Missing
folders are skipped silently. Music ducks while a line plays. Timings and
score thresholds are the constants at the top of `web/src/sound.js`.

## Your progress

Stats and playground databases live in `~/.wgu_study_hub/<course>/`,
created automatically and shared between the web app and the CLI. Delete a
course's folder there for a clean reset; the app itself is untouched. If
you used the original standalone D426 sandbox, its progress is migrated
from `~/.d426_sandbox` automatically on first run.

## Adding a course

Upload the new course's sources to your Claude project and say
"build a course pack for &lt;course&gt;" — the `course-pack-creator` skill
(in `skills/`) runs the whole pipeline: source inventory, blueprint from
the practice test, concepts, generators, a study guide via the
`course-study-guide` skill, and the mandatory quality harness. The result
is one new folder under `courses/`; restart the hub and the card appears.

Packs work for any course type: definition and scenario drills are
universal; math, networking, and statistics courses get computed questions
(parameters generated fresh, answers derived at runtime); programming
courses get code-output questions whose answers the generator computes by
mirroring the snippet's logic. Hands-on consoles are pluggable: every pack
stipulates its playground (`PLAYGROUND = SqlPlayground(...)`, a
`PythonPlayground()`, a course-specific interpreter, or `None` with a
reason), core renders whatever the backend returns, and the selftest
executes every backend's own proof programs before a pack can ship. The
homepage's "planned" perches are yours to edit in `courses/planned.json`.

A pack only ships when `--selftest <slug>` prints "All checks passed" —
the harness executes every generator across many seeds, grades every SQL
reference against its own grader, rejects unanswerable tasks, and checks
full concept coverage.

## Hacking on the UI (optional)

The frontend under `web/` is React 19 + Vite + Tailwind v4, with a
dark/light theme system (night-owl dark is the default; the toggle in the
top bar persists your choice). End users never touch this — the built app
is committed at `core/webdist/` and the Python server serves it. All the
sound machinery (music player, voice lines, idle/session timers) lives in
one module, `web/src/sound.js`, with its tunables at the top.

To change the UI you need Node 22+:

    cd web
    npm install
    npm run dev      # live-reload dev server, proxies APIs to a running hub
    npm run build    # writes core/webdist — commit the result

(`npm run build` empties `core/webdist` and repopulates it, including
everything under `web/public/` — voice `.wav`s, icons, the portrait — so a
local rebuild keeps all media intact.)

`--selftest` verifies `webdist` integrity everywhere, and on machines with
`web/node_modules` present it also boots the built bundle in jsdom and
asserts the rendered page matches each pack's capabilities.

## Fine print

Unofficial personal study tool; not affiliated with or endorsed by WGU or
zyBooks. Question generators re-teach concepts from the course — they do
not reproduce course or exam content.
