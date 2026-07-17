---
name: course-pack-creator
description: Build a complete WGU Study Hub course pack (adaptive OA-style drills, an optional hands-on playground, study guide) for any WGU course from its raw materials — zyBooks/textbook chapter exports, a practice test or pre-assessment coaching report, study sheets. Use this skill whenever the user asks to add a course to their study hub, build a course pack or "node", make drills/a sandbox/a quiz app for a WGU class, or names a course code (D315, D427, C958, D286, D281, C949, ...) or title ("Java Fundamentals", "Linux Foundations", "Calculus I") and wants study tooling like their existing setup. Also use it to audit, repair, or extend an existing pack. The deliverable is a validated course folder for the hub plus a study guide PDF generated via the course-study-guide skill.
---

# Course Pack Creator

You are adding a course to the user's **WGU Study Hub** — a local,
zero-dependency Python app (`wgu_study_hub.py`) that auto-discovers course
folders and gives each one: adaptive exam drills weighted like the real OA,
a mastery map, a study-guide tab, and — where stipulated — a hands-on
playground. The pipeline is the same for EVERY course type: programming,
math/stats/networking, tools and scenarios, gen-ed. Database courses add
one extra layer (sample databases, execution-graded SQL tasks, the SQL
console); those parts are explicitly scoped below and skipped for
everything else.

A "pack" is ONE folder: `courses/<slug>/` containing `course.py`,
`content.py`, and `study_guide.pdf`. The hub discovers it on restart.
Nothing in `core/` is ever edited for a course.

**Prime directive: the harness is the definition of done.** A pack that
does not print "All checks passed." from
`python3 wgu_study_hub.py --selftest <slug>` does not ship. No exceptions,
no "it should work" — run it.

## Step 0 — Acquire the hub source (you are in a fresh session)

Your filesystem does NOT persist between conversations. The hub's code must
be obtained before anything else, in this order:

1. A zip the user uploaded in this conversation (`/mnt/user-data/uploads/`).
   Their local copy is canonical (it has their newest packs); prefer it
   over the project copy when both exist.
2. The project's FULL framework zip — `wgu-study-hub.zip`: `core/`, `web/`,
   `courses/_template/`, `skills/`, `assets/voicelines/` (framework mascot
   media, served at `/media/`, harmless to packs), the root Start/Stop
   launchers, `install.py`, and `wgu_study_hub.py` — plus any
   `<slug>-pack*.zip` course zips under `/mnt/project/`. Assemble: unzip
   the hub, then unzip each pack into `courses/`.
3. **An UPDATE OVERLAY (`wgu-study-hub-update.zip`, or any `*-update.zip`)
   is a patch, NEVER a source tree.** It ships only changed files — no
   harness, no quiz engine, no playgrounds package — and its webdist is
   deliberately stripped of user media, so a tree built from it alone
   fails `--selftest` immediately (framework check:
   `webdist/static/owl-hero.webp`, `owl-head.png`, `favicon.ico` missing).
   Apply an overlay ONLY on top of a full tree from 1 or 2 (unzip full
   tree, unzip overlay over it, then add packs).
4. Loose `study-hub/...` files in project knowledge are REFERENCE ONLY.
   Search results are chunked text with no binaries (webdist media, voice
   audio, mascot images) and no guarantee of completeness — never assemble
   a build tree from them.
5. No full tree available via 1–3 → STOP and ask the user to upload their
   current `study-hub` folder as a zip.

Then: unzip to `/home/claude/study-hub/`, apply any overlay, add the packs,
and immediately run `python3 wgu_study_hub.py --selftest` to prove the
environment and existing packs are healthy BEFORE you build anything.
Framework fingerprint as of v3.1 (July 2026), to sanity-check what you
unzipped: `core/webapp.py` contains `voiceline_manifest` and
`/api/shutdown`; `web/src/sound.js` exists; `Start Study Hub.*` /
`Stop Study Hub.*` launchers and `install.py` sit at the repo root. Study
the worked examples: `courses/d426/` (full SQL course) and
`courses/_template/` (minimal pack + archetype demos, heavily commented).

Never reconstruct hub code from memory, training data, or project-knowledge
chunks. If core files are missing or the selftest fails out of the box,
report it and stop.

## Step 1 — Triage the course (decides everything downstream)

Ask the user (or read the coaching report / degree plan) for:

- **Assessment type.** OA (proctored objective exam) → drills are the
  product; blueprint comes from the practice test. PA (performance
  assessment / project) → drills support concept mastery only; blueprint
  comes from module emphasis; say so in the blurb and set expectations.
- **Capability tier** — pick ONE row:

| Course type (examples from this program)                       | Capabilities |
|----------------------------------------------------------------|--------------|
| Computable technical — C955 stats, C958 calc, C959/C960 discrete, D315 networking (subnetting!), C952 architecture, C949/C950 DSA | MCQ/TF, mostly COMPUTED |
| Programming — D278/C867 scripting, D286/D287/D387 Java, D288 back-end, D276 web | MCQ/TF incl. code-output questions |
| Tool/OS/scenario — D281 Linux, D197 version control, D430 security, D686 OS, D429/D685 AI | MCQ/TF, definition + scenario pools |
| Database w/ SQL labs — D426, D427                               | MCQ/TF + SQL playground + SQL tasks |
| Gen-ed / writing-heavy — D268, D270, C963, D333, C458, D336, D459 | MCQ/TF definition drills (light pack; confirm the user wants one) |

`SAMPLE_DBS` exists only for the database row (it feeds the SQL drill
grader); every other course type never touches it.
Playgrounds are a separate, MANDATORY stipulation: every pack declares
`PLAYGROUND = <backend>` or `PLAYGROUND = None` plus a note — the harness
fails silent packs. The contract, hard boundaries, and the per-course
implementation table live in the **Playgrounds** section below. Pages
render only what the pack stipulates; a course with no playground contains
no console markup at all. Whether a playground gets implemented at all is
the USER'S call — recommend per the table, ask explicitly, record the
answer (see "Who decides" in the Playgrounds section).

## Step 2 — Inventory the sources; trust nothing

- Uploaded course "PDFs" are often **zip archives** of per-page JPEG+text
  pairs (zyBooks print export). Check magic bytes first (`file x.pdf` — a
  `PK` header means zip). Extract and assemble per-page text into one text
  file per chapter/unit before reading.
- Build a full inventory: unit → section number → title. zyBooks has
  **animation-only sections** that are blocked from export — reconstruct
  their facts from surrounding text and the study sheets; never skip
  silently. Verify the inventory against raw source, not a parser's output.
- Use ONLY the uploaded materials for course facts. Your training data
  about a course's structure or emphasis is not evidence.

Then run a coverage audit: every section maps to >=1 concept or an explicit
"not testable" note.

## Step 3 — Blueprint

Classify every practice-test / pre-assessment question by unit. The
normalized distribution IS `CH_WEIGHT` (must sum to 1.0 — harness checks).
No practice test (some PA courses)? Weight by section counts per unit and
note the assumption to the user.

## Step 4 — CONCEPTS (30–40)

One entry per testable idea, keyed to the course's own numbering:

```python
CONCEPTS = {"short-id": {"ch": 3, "ref": "3.4", "name": "Human name"}, ...}
```

`ch` is the top-level unit number (int — whatever the course calls it; set
`"unit_label"` in the manifest to Chapter/Unit/Module/Lesson so the UI reads
right). `ref` shows up in question tags and "review §X" advice, so it must
match the course's real numbering.

## Step 5 — Generators (the craft step)

Every generator is `def g_name(rng, ctx): -> dict`. Use `rng` for ALL
randomness (never `random.` directly, never `hash()` — both break seed
stability). `ctx.q(db, sql)` executes SQL on a fresh DB copy (database
courses only).

**MCQ dict:**
```python
{"concept": "short-id", "type": "mcq", "prompt": str,
 "options": [str, ...],          # >=3, all distinct
 "answer": 0,                    # index into options
 "explain": str}                 # teaches, cites the section's language
```
**TF dict:** `{"concept", "type": "tf", "prompt", "answer": bool, "explain"}`

**Non-negotiable rules** (the harness enforces every mechanical one):
- **Never mirror a practice-test item.** Same concept, new surface —
  different table/values/framing. Packs re-teach; they never reproduce
  course or exam content.
- **Prefer computed answers.** Derive the correct answer at runtime; build
  distractors from the classic mistakes. Per archetype:
  - *Math/stats/discrete*: generate parameters, compute in pure Python
    (fractions/ints; avoid float equality), distractors = sign slip,
    off-by-one, swapped formula.
  - *Networking (D315)*: generate IP/prefix, compute network, broadcast,
    host count in Python — the perfect computed question.
  - *Code-output (Java/Python/JS)*: put the snippet in the prompt; MIRROR
    its logic in plain Python inside the generator so the answer is
    computed. Only use constructs whose semantics match simple Python ints
    (no overflow, integer division only when intended); distractors =
    off-by-one, wrong init, wrong operator. See `g_code_output` in the
    template.
  - *Tool/command (Linux, git)*: scenario → correct command; distractors =
    plausible wrong flags/subcommands; verify every fact against source.
  - *Definitions (all courses)*: (term, definition) pools with same-pool
    distractors; pad small pools so every question has >=3 options.
- **Every random parameter combination must be answerable.** Use vetted
  tuples, not independent choices (lesson from real packs: independently
  chosen breed x height produced zero-row tasks; a start=0 made a
  distractor collide with the answer).
- Every question gets an `explain` that teaches.

Export: `MCQ_GENERATORS = [...]` (and `SQL_GENERATORS = [...]` — an empty
list for every non-database course). 60–110 MCQ generators is the target
for a 3–4 CU OA course (the scale the original D426 pack set); scale down
proportionally for light packs.

### Database courses only — SQL tasks (skip this block for everything else)

**SQL task dict** (copy the `_sqltask` helper from
`courses/d426/content.py`):
```python
{"type": "sql", "concept": str, "db": str, "prompt": str,
 "reference": str,               # correct SQL; graded against itself
 "kind": "select" | "dml" | "ddl",
 "order_matters": bool,          # select: compare row order?
 "verify": str | None,           # dml: SELECT run on user vs reference
                                 #      state; result sets must match
 "ddl_check": dict | None,       # ddl: {"table": "T",
                                 #  "has_columns": [("Col","TYPE"), ...],
                                 #  "pk": ["Col", ...]}   (pk optional)
 "hint": str | None}
```

Two extra rules, harness-enforced:
- DML deletes: pick FK-safe victim rows (no children referencing them),
  or the reference itself fails.
- Verify dialect facts against the source before encoding (MySQL has no
  FULL JOIN or materialized views; TRUNCATE resets AUTO_INCREMENT).

## Step 6 — Study guide (REQUIRED, not optional)

Invoke the **course-study-guide** skill (in this project) on the same
sources. Its PDF output goes to `courses/<slug>/study_guide.pdf`; the hub
serves it in the course's Study guide tab. Do not hand-write a substitute;
do not skip. If the user already has a guide for this course, use theirs.

The guide pipeline's coverage audit produces a SECTION INVENTORY — save it
as `courses/<slug>/inventory.json` (format:
`{"<chapter>": {"sections": {"<ref>": "<title>", ...}}, ...}`). The
harness verifies every concept §ref against it: a pack citing a section
the source doesn't have is a phantom reference and FAILS — "review §X"
advice must point somewhere real. Without the file, refs go unverified
and the harness warns on every run.

## Step 7 — Assemble

Copy `courses/_template/` to `courses/<slug>/` and fill in:

```python
COURSE = {"code": "D315", "slug": "d315", "name": "...", "blurb": "...",
          "status": "active", "badge": "OA BLUEPRINT · ...",
          "unit_label": "Unit",
          "chapter_names": {1: "...", ...},
          "topics": [("subnet", "Subnetting"), ...]}
```

Then the mandatory playground stipulation (full rules in the Playgrounds
section):

```python
PLAYGROUND = None                                        # most courses
PLAYGROUND_NOTE = "MCQ-only OA; no hands-on component."  # required w/ None
# or: from core.playgrounds.python_runner import PythonPlayground
# or: from .coral import CoralPlayground                 # in-pack backend
# or (database courses):
#     from core.playgrounds.sql import SqlPlayground
#     PLAYGROUND = SqlPlayground(SAMPLE_DBS, DB_DESCRIPTIONS,
#                                placeholder="-- branded starter text")
```

Topic keywords are substring-matched against `concept-id + name + ref`
(lowercased) — verify each keyword actually catches its intended concepts.
Remove the template's demo content entirely. Also drop the course's entry
from `courses/planned.json` if it's listed there.

## Step 8 — Gate, then hand-verify

1. `python3 wgu_study_hub.py --selftest <slug>` prints "All checks passed."
   Run it TWICE in separate processes. The full list of what it enforces
   is in the QA section — half the QA is mechanical and already done for
   you; the other half (below) cannot be skipped.
2. `python3 wgu_study_hub.py --list` shows the course with sane counts.
3. Hand-run: `--cli <slug> --quiz 5` (and `--sql 2` if SQL), plus the web
   app — homepage card, every tab, one full drill to the summary screen.
4. Sanity-read 10 questions for correctness, tone, and ref accuracy — the
   harness cannot judge pedagogy or factual fidelity to the course.
5. If you changed `core/` or the shared template AT ALL: render both a
   database course and a capability-less course and inspect the actual
   pages — verify what the user sees, not the conditional you wrote.
   Tabs being right does not prove the panels are.
6. If the pack stipulates a playground: open it in the browser and run at
   least three snippets by hand — one happy path, one error, and (for
   interpreter backends) one infinite loop, which must come back as an
   error block, never a hang.
7. If you changed `core/`, the template, or anything under `web/`: make
   sure the harness ran with node + `web/node_modules` present so the
   BUILT bundle actually executed under jsdom
   (`web/scripts/render_check.mjs` — it fails the run on ANY uncaught JS
   error). An unguarded `addEventListener` on an absent element, or an
   unguarded module-scope side effect, kills the ENTIRE script, and no
   amount of HTML inspection catches it.

## Step 9 — Deliver

- The PRIMARY deliverable is the pack zip: `<slug>-pack.zip` with the
  course folder at its root (unzips into `courses/`). Ship a refreshed
  FULL `wgu-study-hub.zip` when you changed `core/`, `web/`,
  `courses/_template/`, or `skills/` — which, per rule zero, normally
  means never. Never ship a partial `*-update.zip` overlay from a pack
  session; overlays are for framework-only work and they poison Step 0
  for the next session.
- Tell the user: replace their local `study-hub/` (progress is safe — it
  lives in `~/.wgu_study_hub/`), restart the hub, the card appears.
- Remind them to **upload the pack zip (and the hub zip, if it changed)
  to this project's files**. If the project currently holds only an
  `*-update.zip` or loose repo files instead of a current FULL
  `wgu-study-hub.zip`, say so and ask them to upload one — Step 0 depends
  on it. This loop is what keeps the system model-independent.

## QA — the gate, in two halves

### Half 1: enforced mechanically by the harness (trust it; don't re-verify)

`--selftest <slug>` now checks, per pack: **payload & manifest** (field
lint, status, slug↔folder match, blueprint sums to 1.0 with positive
weights, chapter names, dead or numeric topic keywords, pack import
hygiene, `__init__.py`, study guide is a real PDF); **every question
instance** (raw TYPES — options must BE strings, never coerced;
tuple/list/dict/object-repr leaks with code-context awareness;
`{placeholder}`, `%s`, `%%TOKEN%%`, dev markers, mojibake, escaped
`\uXXXX`; length floors; duplicate options; more than 5 options breaks
A–E keys; shuffle-hostile "all of the above"; asymmetric answer giveaways
— answer verbatim in the prompt while no distractor is);
**determinism** (same-seed purity per generator, per-generator
CROSS-PROCESS fingerprints that name offenders, variety warnings);
**SQL tasks** (database courses: reference self-grades, returns rows, junk fails, reference
determinism, db keys valid, prompt/hint lint); **playground**
(stipulation + recorded user decision, selfchecks executed, junk-input
resilience); **coverage** (every concept AND every blueprint chapter
reachable); **selection path** (blueprint drill smoke; every topic
reachable from generatable questions); **render** (tabs ≡ capabilities,
zero unreplaced tokens, dropdown complete against HTML-escaped labels,
stdin visibility per backend, and the page's actual JS executed under
node when node is installed).

Also mechanical: **§ref verification** — every concept ref is checked
for internal consistency (ref's chapter prefix must equal `ch`) and,
when `inventory.json` is present, for EXISTENCE in the source's section
inventory (phantom refs fail). Semantic correctness — that the fact
itself matches the source — remains yours in Half 2.

Escape hatch: a question that legitimately displays raw code or format
strings sets `"lint": "code"` in its dict — pattern lint is skipped,
type enforcement is not. Every generator using it is surfaced as a
WARNING naming it, and per the delivery mandate that warning must be
dispositioned: say WHY pattern lint is wrong for that content. The
bypass is visible by design — using it to silence a true positive is
weakening the gate.

After ANY edit to `core/harness.py`, run `python3 -m core.harness`: the
selfproof plants 18 known defect classes (including the July 2026
tuple-in-prompt / list-as-option screenshot bug) in a synthetic pack and
fails loudly if the harness lost teeth.

### Half 2: what only a human-grade pass catches — required before delivery

1. Read 10+ rendered questions AS A STUDENT: factually correct against
   the SOURCE (not memory), the §ref points where it claims, distractors
   plausible-but-wrong, the explain actually teaches.
2. Full click-through: every tab; one full MCQ drill to the summary; one
   SQL drill if present; mastery map after answering; study-guide tab;
   playground with three hand-run snippets (happy path, error, and the
   infinite-loop case for interpreters).
3. CLI: `--cli <slug> --quiz 5` (and `--sql 2` where applicable).
4. Eyeball one drill question and the summary at screenshot level.

### Delivery mandate

Never present a build with harness errors. Warnings must be listed and
dispositioned in the delivery message ("accepted because…" or "fixed").
Include FIVE sample questions in the delivery message — rendered as
text, drawn from five different generators at fixed seeds — so the user
can spot-check content quality without opening the app. The user's eyes
are the final gate.

## Playgrounds — contract, boundaries, per-course practice

Core owns the console UI, the HTTP plumbing (`/api/run`, `/api/side`,
`/api/reset`), and the harness gate — all language-agnostic. A pack
supplies the backend that defines what "run" means. Backends return DATA
(blocks); core renders it. Backends never emit HTML or JS.

### Who decides: the user, every time

The per-course table below is a set of RECOMMENDATIONS, never a mandate.
Before implementing — or skipping — a playground, ask the user one direct
question carrying the recommendation and the tradeoff, e.g.: "D278 fits an
in-pack Coral interpreter (real hands-on practice, and the biggest build
item in this pack). Want it, or drills-only?" Then:

- Yes → build it, and record the decision in a comment above the
  stipulation: `# Playground approved by user, 2026-07-14`.
- No → `PLAYGROUND = None` with the decision in the note:
  `PLAYGROUND_NOTE = "User chose drills-only (2026-07-14)."`
- No answer yet → do not guess and do not default; the stipulation waits
  on the user.

The harness enforces that a decision was RECORDED and proven; this rule
ensures the decision was the user's.

### The stipulation (mandatory, harness-enforced)

Every `course.py` declares exactly one of:

```python
PLAYGROUND = SqlPlayground(SAMPLE_DBS, DB_DESCRIPTIONS)  # core backend
PLAYGROUND = PythonPlayground()                           # core backend
PLAYGROUND = CoralPlayground()                            # in-pack backend
PLAYGROUND = None
PLAYGROUND_NOTE = "why this course has no hands-on console"  # required w/ None
```

### The backend contract

Duck-typed; subclass `core.playgrounds.PlaygroundBase`. Canonical field
and shape documentation is the docstring of `core/playgrounds/__init__.py`
— read it before writing a backend. Reference implementations:
`core/playgrounds/sql.py` (rich: sidebar, selector, reset) and
`core/playgrounds/python_runner.py` (minimal: subprocess, stdin). Summary:

```
kind, label, placeholder, stdin_enabled
bind(data_dir)                     # lifecycle; re-bindable; scratch under data_dir
run(source, stdin="") -> {"ok", "blocks", "notes", "state"}
sidebar() / selector() -> None or shapes per the port docstring
reset(target=None) -> message      # only if sidebar offers reset
selfcheck() -> [(source, stdin, expected_substring), ...]
```

### Boundaries (non-negotiable)

1. **Stipulate or fail.** A pack silent on `PLAYGROUND` fails the harness — and the stipulation records the user's decision, not the agent's preference.
2. **selfcheck() is the proof.** ≥2 checks for wrapper backends; ≥8 for
   interpreters (one per language construct). The harness executes every
   check; a backend that cannot prove itself does not ship.
3. **Isolation.** Subprocess backends: wall-clock timeout + output cap.
   In-process interpreters: a STEP BUDGET (count evaluation steps, halt
   around 500k) so an infinite loop returns an error block instead of
   hanging the server. No network. Scratch files only under the bound
   `data_dir`.
4. **Placement.** A backend for ONE course lives in that pack
   (`courses/<slug>/`). A backend for two or more courses lives in
   `core/playgrounds/` — and adding it there is a deliberate, user-approved
   core change, never smuggled in alongside a pack.
5. **Semantics from sources only.** Division rules, output formatting,
   loop bounds — every behavior an interpreter implements must be
   traceable to a section of the course material. Comment the section
   ref next to the rule.
6. **Data out, never markup.** If a backend wants UI, it wants a core
   change — propose it.
7. **Never weaken the gate.** A failing selfcheck means fix the backend.

### Per-course practice (this degree plan) — recommendations to present, per "Who decides"

| Course | Backend & placement | Practice |
|---|---|---|
| D426 / D427 (SQL) | `SqlPlayground` — core, done | pass sample dbs + branded placeholder |
| D278 Scripting Foundations | `CoralPlayground` — IN PACK | full outline below |
| C949 / C950 DSA & general practice | `PythonPlayground` — core, done | `PLAYGROUND = PythonPlayground()` |
| D286 / D287 / D387 / D288 (Java) | future core `ProcessPlayground` | detect `javac`/`java` via `shutil.which`; compile `Main.java` in scratch; run with timeout; missing JDK → `run()` returns an error block with an install hint. Propose the core addition BEFORE the first Java course; each Java pack is then one line of config. |
| C867 (C++) | same `ProcessPlayground`, `g++` | identical pattern |
| D197 Version Control | scratch-repo git backend | `bind()` inits a temp repo; allowlist `init add commit status log diff branch checkout merge`; refuse `remote push clone config`; real `git` via `which`, else `None` + note |
| D281 Linux | SIMULATED shell — IN PACK | toy filesystem + exactly the command subset the course teaches; **never** pass anything to the host shell |
| D315 networking, math, stats, discrete | `None` + note | computed drills are the right tool |
| Gen-ed, writing, AI-concept courses | `None` + note | drills only |

### Outline: the D278 Coral interpreter (courses/d278/coral.py)

A real tokenize → parse → evaluate interpreter; no regex-transpile hacks.
Feature checklist — each item traceable to a chapter section AND covered
by a selfcheck:

- integer and float variables, declarations per the course's syntax
- arrays: declaration with size, indexing, size access if taught
- `Get next input` (reads one whitespace-separated token from stdin)
- `Put ... to output` with the course's EXACT newline rules — verify
  against the chapters, do not assume
- arithmetic including integer division and `%` exactly as defined
- comparison and logical operators
- `if` / `elseif` / `else`; `while`; `for`
- function definitions, parameters, `returns`
- comments

`stdin_enabled = True`; step budget ≈500k with a "possible infinite loop"
error block on exhaustion; `selfcheck()` ≥8 including one stdin-fed
program and one integer-division case.

## Landmines (each cost real debugging time — read before building)

- Fresh sessions have NO hub code; `/mnt/project/` is read-only — copy
  before editing.
- `*-update.zip` overlays are patches, NOT source trees (see Step 0):
  built alone, they fail `--selftest` on the framework webdist check by
  design (required media is deliberately absent, restored only by the
  user's overlay). Do not "fix" that failure by regenerating media —
  acquire a full tree instead.
- Project-knowledge copies of the repo are chunked text with no binaries;
  treat them as reference, never as source (July 2026: a UI session had
  to rebuild the tree from them and could not recover `harness.py` or
  `engine.py` at all).
- The built bundle boots a sound system at module scope (a YouTube iframe
  loader, an `/api/voicelines` fetch, interval timers) in
  `web/src/sound.js`. Its guards — try/catch around player creation,
  promise-checked `audio.play()`, `typeof window` gates — are what let
  `render_check.mjs` pass, because jsdom fails the run on ANY uncaught
  error. Touch `web/` without stripping them.
- `PK` magic bytes on a ".pdf" mean a zip of page images; extract, don't
  parse it as a PDF.
- `hash()` seeds vary per process; harness seeds use `sum(name.encode())`.
- Independent random parameters produce unanswerable or self-colliding
  questions.
- Distractor collisions from arithmetic coincidences (`a+b+1 == a*b`).
- SQL packs only: FK parents in DELETE tasks break the reference
  solution.
- SQL packs only: SQLite behavior differs from MySQL facts; the engine
  translates syntax but exam facts come from the source.
- Animation-only zyBooks sections silently vanish from exports.
- Section parsers misread blocked sections — audit against raw source.
- Code-output questions: simulate the exact semantics or don't ask it.
- Never invent course facts from training data; sources only.
- Verifying the mechanism instead of the render ships bugs (July 2026:
  tab buttons were conditional while the SQL panel leaked onto every
  non-database course page). Check the rendered DOM.
- Test assertions can lie too: counting `data-tab=` also matched a JS
  selector, not just buttons. Assert on precise patterns.
- Framework features (new playground kinds, template changes) are
  deliberate `core/` work proposed to the user — never hacked into a pack.
- An unguarded `addEventListener` on an element that a capability removed
  kills the whole page script. Bind through a null-safe helper and execute
  the script under node to prove it.
- `core/_assets.py` is generated; regenerate it via a script file with
  single-escaped newlines and then IMPORT `core.webapp` directly as part
  of verification — the harness's render checks also import the web layer
  and will surface a broken import as an error, but the direct import is
  the fast, unambiguous proof.
- `str()` coercion hides leaked objects: an f-string happily embeds a
  tuple, and a list survives `map(str, …)` distinctness checks. Options
  must BE strings — the harness type-checks raw values (the July 2026
  screenshot bug shipped exactly this way).
- Distractor SET literals (`wrong = {a, b, c}`) iterate in hash order →
  different options per process. Build distractors as ordered lists with
  order-preserving dedupe; the fingerprint check names offenders.
- Deterministic checks beat sampled checks: a probabilistic n=1 probe
  "fails" randomly and erodes trust. Verify reachability exhaustively.
- Phantom §refs are mechanically detectable — wire inventory.json from
  the study-guide audit into the pack. The semantic class (right section,
  wrong fact) stays human; the citation class doesn't have to.
- Calibrate lint against REAL packs before shipping a new check: "identify
  this part of the code" questions legitimately contain their answer
  (flag only asymmetric giveaways), case-only options are the point of
  UPPER()/LOWER() questions, `CONCAT('a', 'b')` is not a leaked tuple,
  and "placeholder" is a normal English word.

## Definition of done

1. Harness passes twice (separate processes).
2. `study_guide.pdf` present in the pack (via course-study-guide skill).
3. CLI + web drills run by hand; 10 questions sanity-read.
4. Homepage card, all tabs, mastery map verified in the browser.
5. Playground decision asked of the user and recorded in the pack;
   stipulation in place; backend selfchecks green in the harness; three
   manual snippets run in the browser (interpreters: including the
   infinite-loop case).
6. Harness errors: zero. Warnings: listed and dispositioned in the
   delivery message. Five seeded sample questions included in the
   delivery for the user's spot-check.
7. Pack zip delivered (plus a refreshed FULL hub zip iff the framework
   changed) AND the user reminded to re-upload to the project — asking
   for a current full `wgu-study-hub.zip` there if the project holds
   only an `*-update.zip` or loose files.
