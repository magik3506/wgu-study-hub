# D278 session — framework migration + Coral playground build

Context for you (the session holding the D278 sources and pack): the hub
framework was upgraded. Playgrounds are no longer hard-coded SQL furniture;
they are a pluggable, pack-stipulated backend behind a language-agnostic
port, and the harness now enforces the stipulation and executes every
backend's proof programs. Your job: migrate the d278 pack onto the new
framework and build the Coral playground backend. Do these steps in order.

**Decision record:** the user explicitly approved the Coral playground
for D278 in the architecture session (2026-07-14); this document is that
record — cite it in a comment above the stipulation. Going forward the
skill requires asking the user before implementing or skipping any
playground; for this pack that question is already answered.

## 0. Clean migration — do not merge

The user is uploading the new `wgu-study-hub.zip`. Discard your old hub
tree entirely; do NOT copy old `core/` files forward or diff-merge them.
Unzip fresh, then move ONLY your `courses/d278/` folder into the new tree.

Run `python3 wgu_study_hub.py --selftest all`. Expected result: D426 and
the template pass; **d278 FAILS** with "pack must stipulate PLAYGROUND".
That failure is the new framework working — it is your to-do list.

## 1. Read before writing

- `skills/course-pack-creator/SKILL.md`, section **"Playgrounds —
  contract, boundaries, per-course practice"** (includes the D278 Coral
  outline). The boundaries there are non-negotiable.
- The port contract: docstring of `core/playgrounds/__init__.py`.
- Both reference backends: `core/playgrounds/sql.py` (rich) and
  `core/playgrounds/python_runner.py` (minimal, stdin-enabled — the
  closer model for Coral).

Rule zero: you will not edit anything under `core/`. If you believe you
need to, stop and tell the user why instead.

## 2. Build `courses/d278/coral.py`

A real tokenize → parse → evaluate interpreter (no regex-transpile
shortcuts), class `CoralPlayground(PlaygroundBase)`:

- `kind = "coral"`, `label = "Coral playground"`, `stdin_enabled = True`,
  and a placeholder showing a small valid Coral program.
- Features, each implemented from the D278 chapters you hold — comment the
  section ref next to each semantic rule: integer/float variables and
  declarations; arrays (declaration with size, indexing, size access if
  taught); `Get next input` (one whitespace-separated token from stdin);
  `Put ... to output` with the chapters' exact newline behavior — verify,
  don't assume; arithmetic including integer division and `%` exactly as
  defined; comparison and logical operators; `if`/`elseif`/`else`,
  `while`, `for`; functions with parameters and `returns`; comments.
- Execution runs in-process, so isolation = a **step budget**: count
  evaluation steps and halt around 500,000 with an error block reading
  "possible infinite loop" — an endless `while` must return, never hang
  the server. Cap output length with a truncation note.
- Output: blocks only — `{"kind": "text"|"ok"|"error", "text": ...}`.
  `run()` returns `{"ok", "blocks", "notes", "state": {}}`. No sidebar,
  no selector (return None — the UI collapses to a full-width console).
- Semantics come from the uploaded chapters ONLY. Your training-data
  memory of Coral is not evidence; where the chapters are silent, match
  the zyBooks simulator behavior described in them, and note the choice.

## 3. Stipulate it

In `courses/d278/course.py`:

```python
from .coral import CoralPlayground
# Playground approved by user, 2026-07-14 (see D278_session_instructions.md)
PLAYGROUND = CoralPlayground()
```

## 4. Prove it

`selfcheck()` must return at least 8 `(source, stdin, expected_substring)`
programs, together covering: output, variables/arithmetic, INTEGER
DIVISION specifically, an stdin-fed `Get next input` program, an
`if/elseif/else` branch, a `while` loop, a `for` loop (if taught), arrays,
and a function call with a return value. The harness executes all of them.

## 5. Gate, then verify the render

1. `python3 wgu_study_hub.py --selftest d278` → "All checks passed."
   Run it twice in separate processes.
2. Start the web app. On the d278 page verify: a **Coral playground** tab;
   the console full-width (no sidebar); the stdin box visible. Run at
   least three programs by hand: a happy path, a syntax error (readable
   error block), and an infinite loop (error block, not a hang).
3. Confirm no SQL artifacts anywhere on the page, and that Exam drill,
   Mastery, and Study guide still work end to end.
4. You changed no core files, so no JS-shim step is required — if you did
   change any, go back to rule zero.

## 6. Out of scope — do not do these

- No execution-graded Coral drill tasks yet: task grading in core is
  SQL-specific (`check_sql_task`). Do not bend it or fork it inside the
  pack. If the user wants graded Coral tasks, that is a core feature to
  propose separately.
- No edits to `core/`, no second playground kinds, no UI/HTML emitted
  from the backend.

## 7. Deliver

Zip the refreshed hub (exclude `__pycache__`) to outputs, present it, and
remind the user to (a) replace their local `study-hub/` — progress is safe
in `~/.wgu_study_hub/` — and (b) re-upload the refreshed zip to the Claude
project files so the next session starts from current state.
