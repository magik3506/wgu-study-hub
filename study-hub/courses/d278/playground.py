"""Coral playground backend for D278 — lives IN THE PACK, per the port's
placement rule: a backend used by exactly one course belongs to that course.
If a second Coral course ever appears, promoting this to core/playgrounds/ is a
deliberate, user-approved core change.

Returns DATA (blocks) only; core owns the rendering.
"""
from core.playgrounds import PlaygroundBase

from .coral import run_coral, STEP_BUDGET

PLACEHOLDER = """\
// Coral — the language D278 actually teaches.
// Press Run. Type program input in the box below the editor.

integer userAge
userAge = Get next input

if userAge < 13
   Put "Child" to output
elseif userAge < 20
   Put "Teen" to output
else
   Put "Adult" to output
Put newline to output

// The classic trap — 9 / 5 is INTEGER division (§2.10)
float f
f = 100 * (9 / 5) + 32
Put "Broken:  " to output
Put f to output
Put newline to output

f = 100 * (9.0 / 5) + 32
Put "Correct: " to output
Put f to output
"""


class CoralPlayground(PlaygroundBase):
    kind = "coral"
    label = "Coral console"
    stdin_enabled = True                      # §2.1 — `x = Get next input`
    placeholder = PLACEHOLDER

    def __init__(self, step_budget=STEP_BUDGET):
        self.step_budget = step_budget

    def bind(self, data_dir):
        # The interpreter is in-process and touches no files, so there is
        # nothing to set up. bind() must still be re-bindable and cheap.
        self.data_dir = data_dir

    # -- run ----------------------------------------------------------
    def run(self, source, stdin=""):
        r = run_coral(str(source), str(stdin))
        blocks, notes = [], []

        if r["output"]:
            blocks.append({"kind": "text", "text": r["output"]})
        if r["truncated"]:
            notes.append("(output truncated — the program printed too much)")

        if r["error"]:
            blocks.append({"kind": "error", "text": r["error"]})
        elif not r["output"]:
            blocks.append({"kind": "ok", "text": "(no output)"})

        if r["steps"]:
            notes.append(f"{r['steps']:,} steps")

        return {"ok": r["ok"], "blocks": blocks, "notes": notes,
                "state": {"steps": r["steps"]}}

    # -- sidebar: runnable examples, one per construct ----------------
    def sidebar(self):
        return {
            "title": "Coral examples",
            "sub": "Click to load a snippet, then press Run. Each one is a "
                   "construct the OA tests.",
            "reset_all": None,
            "groups": [
                {"name": "Expressions", "desc": "Chapter 2", "on": True,
                 "reset": False,
                 "items": [
                     {"label": "Integer vs float division (§2.10)",
                      "title": "The single most-missed rule on the exam",
                      "run": 'Put "10 / 4   = " to output\nPut 10 / 4 to output\n'
                             'Put newline to output\nPut "10 / 4.0 = " to output\n'
                             'Put 10 / 4.0 to output'},
                     {"label": "Modulo (§2.12)",
                      "run": 'Put "23 % 10 = " to output\nPut 23 % 10 to output'},
                     {"label": "Type coercion trap (§2.10)",
                      "title": "A float variable does NOT fix integer division",
                      "run": 'float f\nf = 9 / 5\nPut "9 / 5 stored in a float: " '
                             'to output\nPut f to output'},
                 ]},
                {"name": "Branches & loops", "desc": "Chapters 3-4", "on": True,
                 "reset": False,
                 "items": [
                     {"label": "if / elseif / else (§3.1)",
                      "run": 'integer x\nx = Get next input\nif x < 10\n   Put '
                             '"Too young" to output\nelseif x < 20\n   Put "OK" '
                             'to output\nelse\n   Put "Too old" to output'},
                     {"label": "do-while runs at least once (§4.9)",
                      "run": 'integer x\nx = 4\ndo\n   Put x to output\n   Put " " '
                             'to output\n   x = x - 1\nwhile x > 1'},
                     {"label": "Nested loops multiply (§4.7)",
                      "run": 'integer i\ninteger j\ninteger c\nc = 0\nfor i = 0; '
                             'i < 3; i = i + 1\n   for j = 0; j < 4; j = j + 1\n'
                             '      c = c + 1\nPut "inner ran " to output\nPut c '
                             'to output\nPut " times" to output'},
                     {"label": "Infinite loop (step budget catches it)",
                      "title": "Shows what happens when the loop variable never "
                               "changes",
                      "run": 'integer c\nc = 0\nwhile c < 5\n   Put "Hi" to output'},
                 ]},
                {"name": "Arrays & functions", "desc": "Chapters 5-6", "on": True,
                 "reset": False,
                 "items": [
                     {"label": "Arrays are 0-based (§5.1)",
                      "run": 'integer array(4) userVals\nuserVals[0] = 7\n'
                             'userVals[3] = 9\nPut "size = " to output\nPut '
                             'userVals.size to output\nPut newline to output\n'
                             'Put "last index = " to output\nPut userVals.size - 1 '
                             'to output'},
                     {"label": "Find the max in an array",
                      "run": 'integer array(5) v\nv[0] = 3\nv[1] = 9\nv[2] = 2\n'
                             'v[3] = 7\nv[4] = 5\ninteger i\ninteger maxVal\n'
                             'maxVal = v[0]\nfor i = 1; i < v.size; i = i + 1\n'
                             '   if v[i] > maxVal\n      maxVal = v[i]\nPut "max = " '
                             'to output\nPut maxVal to output'},
                     {"label": "Function returns via its named variable (§6.2)",
                      "run": 'Function ComputeSquare(integer numToSquare) returns '
                             'integer numSquared\n   numSquared = numToSquare * '
                             'numToSquare\n\ninteger r\nr = ComputeSquare(7)\n'
                             'Put r to output'},
                     {"label": "Output concatenates — no spaces (§2.2)",
                      "title": "Three calls print HeyHeyHey, not Hey Hey Hey",
                      "run": 'Function G() returns nothing\n   Put "Hey" to output'
                             '\n\nG()\nG()\nG()'},
                 ]},
            ],
        }

    # -- proof (harness executes every one; >=8 required for interpreters) --
    def selfcheck(self):
        return [
            # §2.10 — both operands integer -> integer division
            ("Put 10 / 4 to output", "", "2"),
            # §2.10 — one float operand -> floating-point division
            ("Put 10 / 4.0 to output", "", "2.5"),
            # §2.10 — the coercion trap from the chapter's own table
            ("float f\nf = 100 * (9 / 5) + 32\nPut f to output", "", "132.0"),
            # §2.12 — modulo
            ("Put 23 % 10 to output", "", "3"),
            # §2.2 — Put adds NO separator; `newline` is a keyword
            ('Put "Hey" to output\nPut newline to output\nPut "Ho" to output',
             "", "Hey\nHo"),
            # §2.1 — Get next input reads one whitespace-separated token
            ("integer x\nx = Get next input\nPut x * 2 to output", "21", "42"),
            # §3.1 — if / elseif / else, indented blocks
            ('integer x\nx = Get next input\nif x < 10\n   Put "low" to output\n'
             'elseif x < 20\n   Put "mid" to output\nelse\n   Put "high" to output',
             "17", "mid"),
            # §4.9 — a do-while ALWAYS runs its body at least once
            ("integer x\nx = 0\ndo\n   Put x to output\n   x = x - 1\nwhile x > 0",
             "", "0"),
            # §4.4 / §4.7 — for loop and nested loops
            ("integer i\ninteger j\ninteger c\nc = 0\nfor i = 0; i < 3; i = i + 1\n"
             "   for j = 0; j < 4; j = j + 1\n      c = c + 1\nPut c to output",
             "", "12"),
            # §5.1 — arrays are 0-based; .size is the count
            ("integer array(4) v\nv[3] = 9\nPut v[3] to output\nPut v.size to "
             "output", "", "94"),
            # §6.2 — the call evaluates to the NAMED RETURN VARIABLE
            ("Function ComputeSquare(integer n) returns integer numSquared\n"
             "   numSquared = n * n\n\nPut ComputeSquare(7) to output", "", "49"),
            # §1.3 — // comment on its own line
            ("// a comment\nPut 5 to output", "", "5"),
            # isolation — an infinite loop must be HALTED, not hang the hub
            ('integer c\nc = 0\nwhile c < 5\n   Put "Hi" to output', "",
             "infinite loop"),
        ]
