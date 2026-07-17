# WGU Study Hub

A local, zero-install study environment for WGU courses: adaptive exam
drills weighted like the real OA, a MySQL-flavored SQL playground (for SQL
courses), hands-on SQL tasks graded by execution, a mastery map, and each
course's study guide — all in one place, all offline.

**Requirements:** Python 3.8+ standard library. Nothing to pip install.
The web UI ships pre-built (React, dark/light theme, night-owl by
default) — running the hub needs no Node, npm, or network.

## Run it

    python3 wgu_study_hub.py                    # web app (opens browser)
    python3 wgu_study_hub.py --cli d426         # terminal REPL + drills
    python3 wgu_study_hub.py --cli d426 --quiz 10
    python3 wgu_study_hub.py --cli d426 --sql 5
    python3 wgu_study_hub.py --selftest         # validate every course pack
    python3 wgu_study_hub.py --list             # show discovered courses

## Layout

    wgu_study_hub.py      the only file you run
    core/                 engine, grader, harness, server — course-agnostic
    core/webdist/         the built web UI (ships with the framework)
    web/                  frontend source (React + Vite + Tailwind) —
                          only needed if you're changing the UI itself
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
is committed at `core/webdist/` and the Python server serves it.

To change the UI you need Node 22+:

    cd web
    npm install
    npm run dev      # live-reload dev server, proxies APIs to a running hub
    npm run build    # writes core/webdist — commit the result

`--selftest` verifies `webdist` integrity everywhere, and on machines with
`web/node_modules` present it also boots the built bundle in jsdom and
asserts the rendered page matches each pack's capabilities.

## Fine print

Unofficial personal study tool; not affiliated with or endorsed by WGU or
zyBooks. Question generators re-teach concepts from the course — they do
not reproduce course or exam content.
