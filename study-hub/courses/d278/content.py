"""D278 — Scripting and Programming Foundations.

Course language is CORAL (a pedagogical flowchart/code language), NOT C++,
despite what the course title suggests. Every snippet here uses Coral syntax
verified against the zyBooks chapters:
    Put x to output      x = Get next input      integer array(5) vals
    if / elseif / else   while / for / do        Function F(...) returns ...

CH_WEIGHT comes from the student's completed pre-assessment (70 questions
classified by chapter), NOT from the textbook's chapter sizes -- the two are
very different. Chapters 1, 10 and 11 drew zero questions on that form; they
get a 3% floor because they are real, testable course content and the OA is a
different sample of the same bank.

Questions are COMPUTED wherever possible: code-output generators mirror the
Coral snippet's logic in plain Python so the answer is derived at runtime and
distractors are the classic mistakes (truncation misapplied, off-by-one, inner
loop counted alone, forgotten concatenation).
"""

CONCEPTS = {
    # --- Ch 1: Introduction -------------------------------------------------
    "data-bits":        {"ch": 1,  "ref": "1.6",  "name": "Data represented as bits (ASCII/Unicode)"},
    "pseudocode":       {"ch": 1,  "ref": "1.10", "name": "Pseudocode and flowchart shapes"},
    "comments-ws":      {"ch": 1,  "ref": "1.3",  "name": "Comments and whitespace"},

    # --- Ch 2: Variables & expressions --------------------------------------
    "variables":        {"ch": 2,  "ref": "2.1",  "name": "Variables and assignment"},
    "identifiers":      {"ch": 2,  "ref": "2.3",  "name": "Identifier naming rules"},
    "arith-expr":       {"ch": 2,  "ref": "2.4",  "name": "Arithmetic expressions and math functions"},
    "int-division":     {"ch": 2,  "ref": "2.10", "name": "Integer division truncates"},
    "type-convert":     {"ch": 2,  "ref": "2.11", "name": "Type conversion and mixed-type division"},
    "modulo":           {"ch": 2,  "ref": "2.12", "name": "Modulo operator"},
    "data-types":       {"ch": 2,  "ref": "2.13", "name": "Choosing a data type"},
    "constants":        {"ch": 2,  "ref": "2.14", "name": "Constants"},

    # --- Ch 3: Branches -----------------------------------------------------
    "branch-structure": {"ch": 3,  "ref": "3.1",  "name": "if / if-else / if-elseif-else"},
    "relational-ops":   {"ch": 3,  "ref": "3.3",  "name": "Equality and relational operators"},
    "logical-ops":      {"ch": 3,  "ref": "3.5",  "name": "Logical operators and ranges"},
    "order-eval":       {"ch": 3,  "ref": "3.6",  "name": "Order of evaluation"},
    "float-compare":    {"ch": 3,  "ref": "3.8",  "name": "Comparing floating-point values"},

    # --- Ch 4: Loops --------------------------------------------------------
    "loop-choice":      {"ch": 4,  "ref": "4.6",  "name": "Choosing while / for / do-while"},
    "loop-trace":       {"ch": 4,  "ref": "4.3",  "name": "Tracing loop output"},
    "do-while":         {"ch": 4,  "ref": "4.9",  "name": "do-while runs at least once"},
    "nested-loops":     {"ch": 4,  "ref": "4.7",  "name": "Nested loops multiply"},
    "loop-anatomy":     {"ch": 4,  "ref": "4.2",  "name": "Loop expression and initialization"},
    "infinite-loop":    {"ch": 4,  "ref": "4.2",  "name": "Infinite loops"},

    # --- Ch 5: Arrays -------------------------------------------------------
    "array-index":      {"ch": 5,  "ref": "5.1",  "name": "Array indices are 0-based"},
    "array-iterate":    {"ch": 5,  "ref": "5.4",  "name": "Iterating through an array"},
    "array-swap":       {"ch": 5,  "ref": "5.5",  "name": "Swapping two variables"},

    # --- Ch 6: Functions ----------------------------------------------------
    "param-vs-arg":     {"ch": 6,  "ref": "6.1",  "name": "Parameter vs argument"},
    "func-return":      {"ch": 6,  "ref": "6.2",  "name": "Return values"},
    "func-output":      {"ch": 6,  "ref": "6.5",  "name": "Output from repeated function calls"},
    "func-naming":      {"ch": 6,  "ref": "6.5",  "name": "Valid function names"},
    "modular-dev":      {"ch": 6,  "ref": "6.3",  "name": "Modular and incremental development"},

    # --- Ch 7: Algorithms ---------------------------------------------------
    "algorithm-def":    {"ch": 7,  "ref": "7.1",  "name": "What an algorithm is"},
    "comp-problem":     {"ch": 7,  "ref": "7.2",  "name": "Computational problems (input/question/output)"},
    "algo-efficiency":  {"ch": 7,  "ref": "7.3",  "name": "Algorithm efficiency, best and worst case"},
    "search-linear":    {"ch": 7,  "ref": "7.4",  "name": "Linear search"},
    "search-binary":    {"ch": 7,  "ref": "7.5",  "name": "Binary search"},
    "sorting":          {"ch": 7,  "ref": "7.6",  "name": "Sorting by swapping"},
    "algo-ordering":    {"ch": 7,  "ref": "7.1",  "name": "Ordering the steps of an algorithm"},

    # --- Ch 8: Design process -----------------------------------------------
    "sdlc-phases":      {"ch": 8,  "ref": "8.1",  "name": "SDLC phases"},
    "sdlc-scenario":    {"ch": 8,  "ref": "8.1",  "name": "Mapping a scenario to its SDLC phase"},
    "objects":          {"ch": 8,  "ref": "8.2",  "name": "Objects group data and operations"},
    "uml-diagrams":     {"ch": 8,  "ref": "8.3",  "name": "UML diagram types and purposes"},
    "uml-phase-map":    {"ch": 8,  "ref": "8.4",  "name": "UML diagrams across SDLC phases"},
    "waterfall-agile":  {"ch": 8,  "ref": "8.5",  "name": "Waterfall vs agile"},

    # --- Ch 9: Languages & libraries ----------------------------------------
    "compiled-interp":  {"ch": 9,  "ref": "9.1",  "name": "Compiled vs interpreted languages"},
    "typing":           {"ch": 9,  "ref": "9.1",  "name": "Static vs dynamic typing"},
    "lang-kinds":       {"ch": 9,  "ref": "9.1",  "name": "Object-oriented and markup languages"},
    "libraries":        {"ch": 9,  "ref": "9.2",  "name": "Programming libraries"},

    # --- Ch 10: Troubleshooting ---------------------------------------------
    "troubleshoot":     {"ch": 10, "ref": "10.1", "name": "Hypothesis and test cycle"},
    "hypothesis-order": {"ch": 10, "ref": "10.3", "name": "Ordering and narrowing hypotheses"},

    # --- Ch 11: Debugging ---------------------------------------------------
    "debug-output":     {"ch": 11, "ref": "11.1", "name": "Debugging with output statements"},
    "bug-types":        {"ch": 11, "ref": "11.2", "name": "Calculation, logic, and loop errors"},
}

# Derived from the completed pre-assessment (70 items classified by chapter),
# with a 3% floor for chapters that drew zero items on that form.
CH_WEIGHT = {
    1: 0.027, 2: 0.142, 3: 0.039, 4: 0.090, 5: 0.027, 6: 0.103,
    7: 0.129, 8: 0.208, 9: 0.181, 10: 0.027, 11: 0.027,
}


# =========================================================================
# helpers
# =========================================================================
def _pick(rng, pool, n_wrong=3):
    """(term, correct, [wrong...]) -> mcq options with same-pool distractors."""
    item = rng.choice(pool)
    others = [x for x in pool if x[1] != item[1]]
    rng.shuffle(others)
    wrong = [o[1] for o in others[:n_wrong]]
    opts = [item[1]] + wrong
    return item, opts


def _pad(wrong, truth, kind="int"):
    """Pad a distractor list to 3 unique entries that never collide with truth.

    BOUNDED BY CONSTRUCTION. The bug this replaces: the candidate was derived
    from len(wrong), so when a candidate collided, wrong never grew, len(wrong)
    never changed, and the loop spun forever. Here k ALWAYS increments.
    """
    out = [w for w in dict.fromkeys(wrong) if w != truth]
    k = 1
    while len(out) < 3 and k <= 60:
        if kind == "float":
            try:
                cand = f"{float(truth) + k:.1f}"
            except ValueError:
                cand = f"{truth}{k}"
        elif kind == "text":
            cand = f"{truth} {'?' * k}"
        else:
            try:
                cand = str(int(truth) + k)
            except ValueError:
                cand = f"{truth}{k}"
        if cand != truth and cand not in out:
            out.append(cand)
        k += 1
    return out[:3]


def _shuffle_answer(rng, correct, wrong):
    """Return (options, answer_index) with the correct option placed randomly."""
    opts = [correct] + list(wrong)
    rng.shuffle(opts)
    return opts, opts.index(correct)


# =========================================================================
# Ch 1 — Introduction
# =========================================================================
def g_bits_binary(rng, ctx):
    """COMPUTED: binary -> decimal."""
    n = rng.choice([9, 11, 12, 13, 18, 20, 22, 25, 26, 28])
    b = bin(n)[2:]
    wrong = [n + 1, n - 1, int(b[::-1], 2)]
    wrong = [w for w in wrong if w != n]
    wrong = [str(w) for w in list(wrong)[:2]] + [str(n * 2)]
    wrong = [w for w in dict.fromkeys(wrong) if w != str(n)][:3]
    opts, idx = _shuffle_answer(rng, str(n), wrong)
    return {"concept": "data-bits", "type": "mcq",
            "prompt": f"Inside a computer all data is stored as bits. What is "
                      f"the binary number {b} as a decimal number?",
            "options": opts, "answer": idx,
            "explain": f"Binary is base-2. {b} = {n} in decimal. Every value in "
                       f"memory — numbers, characters, images — is ultimately a "
                       f"sequence of 0s and 1s."}


def g_ascii_unicode(rng, ctx):
    pool = [
        ("ASCII bit width", "ASCII uses 7 bits, giving 128 characters"),
        ("Unicode", "Unicode uses more bits and covers 100,000+ characters"),
        ("A bit", "A bit is a single 0 or 1; 8 bits make a byte"),
        ("Text storage", "A word is stored as a sequence of bit codes, one per character"),
    ]
    item, opts = _pick(rng, pool)
    opts, idx = _shuffle_answer(rng, item[1], [o for o in opts if o != item[1]])
    return {"concept": "data-bits", "type": "mcq",
            "prompt": f"Which statement correctly describes {item[0]}?",
            "options": opts, "answer": idx,
            "explain": f"{item[1]}. ASCII is the small 7-bit/128-character "
                       f"standard; Unicode is the large one."}


def g_flowchart_shape(rng, ctx):
    shapes = [
        ("an input or output statement", "Parallelogram"),
        ("the start or end of a program", "Oval"),
        ("a process or assignment", "Rectangle"),
        ("a decision (a branch)", "Diamond"),
    ]
    role, shape = rng.choice(shapes)
    wrong = [s for _, s in shapes if s != shape]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, shape, wrong[:3])
    return {"concept": "pseudocode", "type": "mcq",
            "prompt": f"In a flowchart, which shape represents {role}?",
            "options": opts, "answer": idx,
            "explain": f"{shape} = {role}. The four shapes: oval = start/end, "
                       f"parallelogram = input/output, rectangle = process, "
                       f"diamond = decision."}


def g_pseudocode_def(rng, ctx):
    correct = "An informal description of a program, meant for humans to read"
    wrong = ["A language that uses tags to format text",
             "Machine code produced by a compiler",
             "A diagram showing the order of messages between components"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "pseudocode", "type": "mcq",
            "prompt": "What is pseudocode?",
            "options": opts, "answer": idx,
            "explain": "Pseudocode is an informal, human-readable sketch of a "
                       "program. It is not executable — it exists to make the "
                       "logic easy to follow."}


def g_comments_ws(rng, ctx):
    truth = rng.choice([True, False])
    if truth:
        stmt = ("Whitespace is mostly ignored by the computer, but matters a "
                "great deal for human readability.")
    else:
        stmt = ("A comment is executed by the computer just like any other "
                "statement.")
    return {"concept": "comments-ws", "type": "tf",
            "prompt": stmt, "answer": truth,
            "explain": "Comments (// like this) are for humans and are ignored "
                       "by the computer. Whitespace is likewise mostly ignored "
                       "at execution but is essential to readability."}


# =========================================================================
# Ch 2 — Variables & expressions
# =========================================================================
def g_int_division(rng, ctx):
    """COMPUTED: int/int truncates. Distractors = the float answer + rounding."""
    a, b = rng.choice([(7, 2), (9, 2), (10, 4), (17, 5), (13, 4), (25, 6), (11, 3)])
    truth = a // b                      # Coral: both ints -> truncates
    exact = a / b
    wrong = [f"{exact:.1f}", str(truth + 1), f"{round(exact)}"]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "int-division", "type": "mcq",
            "prompt": f"Given integer x = {a} and integer y = {b}.\n"
                      f"What is the value of the expression  x / y ?",
            "options": opts, "answer": idx,
            "explain": f"BOTH operands are integers, so division truncates (the "
                       f"fraction is dropped): {a} / {b} = {truth}, not {exact:.2f}. "
                       f"Truncation applies only when both operands are integers."}


def g_mixed_division(rng, ctx):
    """COMPUTED: one float operand -> float division. The classic trap: students
    who over-learned truncation apply it here and get the wrong answer."""
    x, f, y = rng.choice([(6, 4.0, 1), (3, 2.0, 4), (9, 2.0, 1), (5, 2.0, 3),
                          (7, 4.0, 2), (10, 4.0, 1), (15, 2.0, 2)])
    truth = x / f + y                       # float division, then add
    trunc = x // int(f) + y                 # WRONG: truncated as if int/int
    wrong = [f"{float(trunc):.1f}", f"{truth + 1:.1f}", f"{x / f:.1f}"]
    wrong = [w for w in wrong if w != f"{truth:.1f}"]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, f"{truth:.1f}", 'float')
    opts, idx = _shuffle_answer(rng, f"{truth:.1f}", wrong[:3])
    return {"concept": "type-convert", "type": "mcq",
            "prompt": f"Given integer x = {x} and integer y = {y}.\n"
                      f"What is the value of the expression  (x / {f}) + y ?",
            "options": opts, "answer": idx,
            "explain": f"{f} is a float, so the division is FLOAT division: "
                       f"{x} / {f} = {x/f}. Then + {y} = {truth}. Truncation fires "
                       f"only when BOTH operands are integers — a decimal point "
                       f"anywhere in the division switches you to float math. "
                       f"(Truncating here would wrongly give {float(trunc)}.)"}


def g_modulo(rng, ctx):
    """COMPUTED: remainder."""
    a, b = rng.choice([(17, 5), (23, 4), (19, 6), (31, 7), (14, 3), (29, 8)])
    truth = a % b
    wrong = [str(a // b), str(truth + 1), str(b - truth)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "modulo", "type": "mcq",
            "prompt": f"What is the value of  {a} % {b} ?",
            "options": opts, "answer": idx,
            "explain": f"% is the modulo (remainder) operator. {a} / {b} is "
                       f"{a//b} remainder {truth}, so {a} % {b} = {truth}. "
                       f"(/ would give the quotient {a//b}.)"}


def g_modulo_use(rng, ctx):
    d = rng.choice([2, 3, 5, 10])
    word = {2: "even", 3: "evenly divisible by 3", 5: "evenly divisible by 5",
            10: "evenly divisible by 10"}[d]
    correct = f"x % {d} == 0"
    wrong = [f"x / {d} == 0", f"x * {d} == 0", f"x - {d} == 0"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "modulo", "type": "mcq",
            "prompt": f"Which expression tests whether integer x is {word}?",
            "options": opts, "answer": idx,
            "explain": f"A number is {word} exactly when dividing by {d} leaves "
                       f"NO remainder, i.e. x % {d} == 0. Use % (remainder), not "
                       f"/ (quotient)."}


def g_precedence(rng, ctx):
    """COMPUTED: order of evaluation with a float to avoid truncation ambiguity."""
    a, b, c = rng.choice([(2, 3, 4), (5, 2, 3), (4, 5, 2), (6, 2, 5), (3, 4, 6)])
    truth = a + b * c                      # * before +
    wrong = [str((a + b) * c), str(a * b + c), str(a + b + c)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "arith-expr", "type": "mcq",
            "prompt": f"What does the expression  {a} + {b} * {c}  evaluate to?",
            "options": opts, "answer": idx,
            "explain": f"* binds tighter than +, so {b} * {c} = {b*c} happens "
                       f"first, then + {a} gives {truth}. Left-to-right without "
                       f"precedence would wrongly give {(a+b)*c}. Parentheses "
                       f"override this."}


def g_math_function(rng, ctx):
    kind = rng.choice(["sqrt", "pow", "abs"])
    if kind == "sqrt":
        n = rng.choice([16, 25, 36, 49, 64, 81])
        call = f"SquareRoot({float(n)})"
        truth = f"{float(int(n ** 0.5)):.1f}"
        wrong = [f"{float(n/2):.1f}", f"{float(n*2):.1f}", f"{float(int(n**0.5))+1:.1f}"]
    elif kind == "pow":
        b, e = rng.choice([(2.0, 3.0), (3.0, 2.0), (2.0, 4.0), (5.0, 2.0)])
        call = f"RaiseToPower({b}, {e})"
        truth = f"{b ** e:.1f}"
        wrong = [f"{b * e:.1f}", f"{b + e:.1f}", f"{e ** b:.1f}"]
    else:
        n = rng.choice([-4, -7, -12, -3])
        call = f"AbsoluteValue({n})"
        truth = str(abs(n))
        wrong = [str(n), str(-abs(n) - 1), str(abs(n) + 1)]
    wrong = [w for w in dict.fromkeys(wrong) if w != truth][:3]
    opts, idx = _shuffle_answer(rng, truth, wrong[:3])
    return {"concept": "arith-expr", "type": "mcq",
            "prompt": f"What does  {call}  evaluate to?",
            "options": opts, "answer": idx,
            "explain": f"{call} = {truth}. Built-in math functions take their "
                       f"arguments in parentheses and evaluate to a value, so a "
                       f"call can be used anywhere an expression is allowed."}


def g_identifier_valid(rng, ctx):
    good = rng.choice(["totalCount2", "userAge", "num_items", "maxValue",
                       "avgScore3", "item_count"])
    bad = [rng.choice(["2ndAttempt", "3total", "9lives"]),
           rng.choice(["user-age", "total-count", "max value"]),
           rng.choice(["integer", "while", "if"])]
    opts, idx = _shuffle_answer(rng, good, bad)
    return {"concept": "identifiers", "type": "mcq",
            "prompt": "Which is a VALID identifier for a variable?",
            "options": opts, "answer": idx,
            "explain": f"'{good}' is valid. Identifiers may contain letters, "
                       f"digits and underscores, but may NOT start with a digit, "
                       f"may not contain hyphens or spaces, and may not be a "
                       f"reserved word. They are also case-sensitive."}


def g_identifier_rule(rng, ctx):
    truth = rng.choice([True, False])
    stmt = ("An identifier may contain digits, but may not begin with one."
            if truth else
            "Identifiers are case-insensitive, so numCars and numcars refer to "
            "the same variable.")
    return {"concept": "identifiers", "type": "tf",
            "prompt": stmt, "answer": truth,
            "explain": "Identifiers may contain letters, digits and underscores "
                       "but cannot START with a digit, and they ARE case-"
                       "sensitive: numCars and numcars are two different names."}


def g_data_type(rng, ctx):
    cases = [
        ("a person's height in meters", "Float"),
        ("the number of seats in a stadium", "Integer"),
        ("whether an alarm is currently armed", "Boolean"),
        ("a customer's full name", "String"),
        ("the number of planes in a hangar", "Integer"),
        ("the price of an item in dollars and cents", "Float"),
        ("whether a user is logged in", "Boolean"),
        ("a single letter grade", "Character"),
    ]
    what, correct = rng.choice(cases)
    wrong = [t for t in ["Integer", "Float", "Boolean", "String", "Character"]
             if t != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "data-types", "type": "mcq",
            "prompt": f"A variable should hold {what}.\nWhich data type should "
                      f"the variable be?",
            "options": opts, "answer": idx,
            "explain": f"{correct} is right for {what}. Integer = whole numbers, "
                       f"Float = fractional values, Boolean = true/false, "
                       f"String = text, Character = one symbol."}


def g_constants(rng, ctx):
    cases = [
        ("the number of inches in a foot, which is 12", "inchesPerFoot", "integer"),
        ("the number of hours in a day, which is 24", "hoursPerDay", "integer"),
        ("the number of days in a week, which is 7", "daysPerWeek", "integer"),
    ]
    what, name, typ = rng.choice(cases)
    correct = f"Constant {typ} {name}"
    wrong = [f"Variable {typ} {name}",
             f"Constant {typ} 12" if "inches" in what else f"Constant {typ} 24",
             f"Variable float userValue"]
    wrong = [w for w in dict.fromkeys(wrong) if w != correct][:3]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "constants", "type": "mcq",
            "prompt": f"A program repeatedly uses {what}.\nHow should the item "
                      f"holding that value be declared?",
            "options": opts, "answer": idx,
            "explain": f"It never changes, so it is a CONSTANT — and it needs a "
                       f"descriptive NAME, not a literal number. Hence "
                       f"'{correct}'. Constants make code readable and prevent "
                       f"accidental reassignment."}


def g_constant_vs_cast(rng, ctx):
    """Targets a real confusion: cast (changes TYPE) vs constant (locks VALUE)."""
    term = rng.choice(["type cast", "constant"])
    defs = {"type cast": "Explicitly converts a value from one data type to another",
            "constant": "A named value that cannot be changed after it is set"}
    correct = defs[term]
    wrong = [defs["constant" if term == "type cast" else "type cast"],
             "A named location in memory whose value may change",
             "The remainder left after integer division"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "type-convert" if term == "type cast" else "constants",
            "type": "mcq",
            "prompt": f"What is a {term}?",
            "options": opts, "answer": idx,
            "explain": f"A {term}: {correct.lower()}. Keep the pair straight — a "
                       f"CAST changes a value's TYPE; a CONSTANT locks a value's "
                       f"CONTENTS. They are easy to swap under pressure."}


def g_variables_assign(rng, ctx):
    """COMPUTED: assignment is right-to-left, and x = x + n is legal."""
    start, add, mul = rng.choice([(5, 3, 2), (4, 6, 3), (7, 2, 2), (10, 5, 2)])
    truth = (start + add) * mul
    wrong = [str(start + add * mul), str(start + add), str(start * mul + add)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    code = (f"integer x\n"
            f"x = {start}\n"
            f"x = x + {add}\n"
            f"x = x * {mul}\n"
            f"Put x to output")
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "variables", "type": "mcq",
            "prompt": "What does this Coral program put to output?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"Assignment works right-to-left, one statement at a time: "
                       f"x = {start}; then x = {start}+{add} = {start+add}; then "
                       f"x = {start+add}*{mul} = {truth}. 'x = x + n' is not "
                       f"algebra — it re-stores a new value in x."}


def g_divide_by_zero(rng, ctx):
    correct = "A divide-by-zero error occurs at runtime"
    wrong = ["The expression evaluates to 0",
             "The expression evaluates to the first operand",
             "The compiler silently ignores the statement"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "int-division", "type": "mcq",
            "prompt": "While a program is running, the second operand of the / "
                      "operator turns out to be 0. What happens?",
            "options": opts, "answer": idx,
            "explain": "Dividing by zero is a RUNTIME error — it terminates the "
                       "program. It is not caught for you and does not quietly "
                       "produce 0, which is why input that could be zero must be "
                       "checked before dividing."}


# =========================================================================
# Ch 3 — Branches
# =========================================================================
def g_branch_choice(rng, ctx):
    cases = [
        ("exactly one of several mutually exclusive cases applies",
         "An if-elseif-else statement"),
        ("a single optional action should happen only when a condition is true",
         "A single if statement"),
        ("two mutually exclusive paths must be chosen between",
         "An if-else statement"),
        ("several independent conditions can each be true at the same time",
         "Multiple separate if statements"),
    ]
    what, correct = rng.choice(cases)
    wrong = [c for _, c in cases if c != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "branch-structure", "type": "mcq",
            "prompt": f"Which branch structure should be used when {what}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. if = one optional action; if-else = two "
                       f"exclusive paths; if-elseif-else = exactly one of many; "
                       f"separate ifs = independent conditions that can co-occur."}


def g_relational_op(rng, ctx):
    ops = [("equal to", "=="), ("not equal to", "!="),
           ("less than or equal to", "<="), ("greater than or equal to", ">=")]
    meaning, correct = rng.choice(ops)
    wrong = [o for _, o in ops if o != correct] + ["="]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "relational-ops", "type": "mcq",
            "prompt": f"Which operator tests whether one value is {meaning} another?",
            "options": opts, "answer": idx,
            "explain": f"'{meaning}' is {correct}. Note = is ASSIGNMENT (store a "
                       f"value), while == is EQUALITY (compare). Confusing the two "
                       f"is one of the most common errors."}


def g_assignment_vs_equality(rng, ctx):
    which = rng.choice(["=", "=="])
    correct = "Assignment" if which == "=" else "Equality"
    wrong = [w for w in ["Assignment", "Equality", "Logical", "Arithmetic"]
             if w != correct]
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    sample = "count = 20" if which == "=" else "count == 20"
    return {"concept": "relational-ops", "type": "mcq",
            "prompt": f"What kind of operator is the {which} in  {sample} ?",
            "options": opts, "answer": idx,
            "explain": f"{which} is the {correct.lower()} operator. A single = "
                       f"STORES a value into a variable; a double == COMPARES two "
                       f"values and evaluates to true or false."}


def g_range_condition(rng, ctx):
    lo, hi = rng.choice([(18, 24), (21, 65), (13, 19), (1, 5), (30, 40)])
    correct = f"(x >= {lo}) and (x <= {hi})"
    wrong = [f"(x >= {lo}) or (x <= {hi})",
             f"(x > {lo}) and (x < {hi})",
             f"(x < {lo}) or (x > {hi})"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "logical-ops", "type": "mcq",
            "prompt": f"Which expression is true for exactly the values of x from "
                      f"{lo} through {hi}, inclusive?",
            "options": opts, "answer": idx,
            "explain": f"Both bounds must hold at once, so the operator is AND, "
                       f"and 'inclusive' means >= and <=: {correct}. Using OR "
                       f"would be true for almost every number; using > and < "
                       f"would wrongly exclude {lo} and {hi}."}


def g_logical_op(rng, ctx):
    ops = [("and", "both sides are true"),
           ("or", "at least one side is true"),
           ("not", "it flips true to false and false to true")]
    op, meaning = rng.choice(ops)
    wrong = [m for _, m in ops if m != meaning] + ["the two sides are equal"]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, meaning, wrong[:3])
    return {"concept": "logical-ops", "type": "mcq",
            "prompt": f"The logical operator '{op}' evaluates to true when...",
            "options": opts, "answer": idx,
            "explain": f"'{op}' is true when {meaning}. Logical operators treat "
                       f"their operands as true/false and evaluate to true/false."}


def g_order_eval(rng, ctx):
    correct = "( )  →  not  →  * / %  →  + −  →  < <= > >=  →  == !=  →  and  →  or"
    wrong = ["and  →  or  →  ( )  →  * / %  →  + −",
             "+ −  →  * / %  →  ( )  →  and  →  or",
             "== !=  →  ( )  →  + −  →  * / %  →  not"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "order-eval", "type": "mcq",
            "prompt": "Which lists the order of evaluation from HIGHEST "
                      "precedence to lowest?",
            "options": opts, "answer": idx,
            "explain": "Parentheses first, then not, then arithmetic (* / % "
                       "before + −), then relational, then equality, then and, "
                       "then or. Use parentheses to make intent explicit rather "
                       "than relying on memory."}


def g_paren_purpose(rng, ctx):
    correct = "To group subexpressions so they are evaluated first"
    wrong = ["To convert a value to a floating-point number",
             "To mark the beginning of a comment",
             "To declare a constant"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "order-eval", "type": "mcq",
            "prompt": "What is the purpose of parentheses in a programming "
                      "expression?",
            "options": opts, "answer": idx,
            "explain": "Parentheses group subexpressions and override the default "
                       "precedence, forcing what is inside them to be evaluated "
                       "first."}


def g_float_compare(rng, ctx):
    correct = ("Check that the absolute value of their difference is less than "
               "a small tolerance")
    wrong = ["Compare them directly with ==, since floats compare exactly",
             "Convert both to integers, then compare with ==",
             "Compare them with the % operator"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "float-compare", "type": "mcq",
            "prompt": "Two floating-point values must be compared to see whether "
                      "they are effectively equal. What is the recommended "
                      "approach?",
            "options": opts, "answer": idx,
            "explain": "Tiny rounding errors make floats that look equal differ "
                       "in their lowest bits, so == is unreliable. Test instead "
                       "that AbsoluteValue(a - b) < 0.0001. Converting to "
                       "integers would throw away the fractional part entirely."}


# =========================================================================
# Ch 4 — Loops
# =========================================================================
def g_loop_choice(rng, ctx):
    cases = [
        ("a message must be printed exactly 12 times", "For loop"),
        ("numbers are read and summed until the user enters -1, and the count "
         "of inputs is not known in advance", "While loop"),
        ("a password prompt must appear at least once, then repeat until the "
         "password is correct", "Do-while loop"),
        ("a menu must be shown once and then repeatedly until the user quits",
         "Do-while loop"),
        ("every element of a 10-element array must be visited", "For loop"),
    ]
    what, correct = rng.choice(cases)
    wrong = [c for c in ["For loop", "While loop", "Do-while loop", "If-else branch"]
             if c != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "loop-choice", "type": "mcq",
            "prompt": f"Which control structure is most appropriate when {what}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. FOR = a known/counted number of iterations. "
                       f"WHILE = repeat until a condition changes, count unknown, "
                       f"may run 0 times. DO-WHILE = body runs first, so it always "
                       f"executes at least once."}


def g_do_while_trace(rng, ctx):
    """COMPUTED: mirrors the Coral do-while in Python. do-while runs >= 1 time."""
    start, floor_ = rng.choice([(4, 1), (5, 2), (3, 1), (6, 3), (5, 1)])
    x, out = start, []
    while True:                          # do { ... } while (x > floor_)
        out.append(x)
        x -= 1
        if not x > floor_:
            break
    truth = " ".join(str(v) for v in out)
    # classic mistakes
    as_while = []                        # treated as a pre-test while loop
    x2 = start
    while x2 > floor_:
        as_while.append(x2)
        x2 -= 1
    one_extra = out + [out[-1] - 1]
    wrong = [" ".join(map(str, as_while)),
             " ".join(map(str, one_extra)),
             " ".join(map(str, out[1:]))]
    wrong = [w for w in wrong if w != truth]
    wrong = [w for w in wrong if w][:3]
    code = (f"x = {start}\n"
            f"do\n"
            f"   Put x to output\n"
            f"   Put \" \" to output\n"
            f"   x = x - 1\n"
            f"while x > {floor_}")
    opts, idx = _shuffle_answer(rng, truth, wrong[:3])
    return {"concept": "do-while", "type": "mcq",
            "prompt": "What is put to output by this Coral pseudocode?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"A do-while runs the BODY FIRST and checks the condition "
                       f"AFTER, so it always executes at least once. Trace: "
                       f"{truth}. The loop stops as soon as x > {floor_} is false."}


def g_while_trace(rng, ctx):
    """COMPUTED: doubling/accumulating while loop."""
    start, limit = rng.choice([(1, 20), (2, 30), (1, 40), (3, 50), (2, 60)])
    v, out = start, []
    while v < limit:
        out.append(v)
        v *= 2
    truth = " ".join(map(str, out))
    wrong = [" ".join(map(str, out + [v])),          # ran one time too many
             " ".join(map(str, out[1:])),            # missed the first
             " ".join(map(str, [x * 2 for x in out]))]
    wrong = [w for w in wrong if w != truth]
    wrong = [w for w in wrong if w][:3]
    code = (f"v = {start}\n"
            f"while v < {limit}\n"
            f"   Put v to output\n"
            f"   Put \" \" to output\n"
            f"   v = v * 2")
    opts, idx = _shuffle_answer(rng, truth, wrong[:3])
    return {"concept": "loop-trace", "type": "mcq",
            "prompt": "What is put to output by this Coral pseudocode?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"A while loop checks the condition BEFORE each pass. v "
                       f"doubles each time and the loop stops the moment v is no "
                       f"longer < {limit}. Output: {truth}."}


def g_for_sum(rng, ctx):
    """COMPUTED: for-loop accumulation."""
    n = rng.choice([4, 5, 6, 7])
    truth = sum(range(n))                 # i = 0 .. n-1
    off_by_one = sum(range(n + 1))        # wrongly included i == n
    from_one = sum(range(1, n))           # started at 1
    wrong = [str(off_by_one), str(from_one), str(truth + n)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    code = (f"integer i\n"
            f"integer sum\n"
            f"sum = 0\n"
            f"for i = 0; i < {n}; i = i + 1\n"
            f"   sum = sum + i\n"
            f"Put sum to output")
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "loop-trace", "type": "mcq",
            "prompt": "What does this Coral program put to output?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"i takes the values 0..{n-1} (the condition is i < {n}, so "
                       f"{n} itself never runs). Sum = {' + '.join(map(str, range(n)))} "
                       f"= {truth}. Including {n} would wrongly give {off_by_one}."}


def g_nested_loops(rng, ctx):
    """COMPUTED: outer x inner. Classic miss = reporting the inner count alone."""
    r, c = rng.choice([(3, 4), (4, 5), (2, 6), (5, 3), (3, 7), (4, 4)])
    truth = r * c
    wrong = [str(c), str(r), str(r + c)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    code = (f"for i = 0; i < {r}; i = i + 1\n"
            f"   for j = 0; j < {c}; j = j + 1\n"
            f"      Put \"*\" to output")
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "nested-loops", "type": "mcq",
            "prompt": "How many times does the inner statement execute?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"For EVERY single pass of the outer loop, the inner loop "
                       f"runs to completion. Outer runs {r} times; each time the "
                       f"inner runs {c} times. {r} × {c} = {truth}. Nested loop "
                       f"iterations MULTIPLY — reporting just {c} counts only the "
                       f"inner loop."}


def g_loop_anatomy(rng, ctx):
    part = rng.choice(["expression", "initialization", "update"])
    var, limit = rng.choice([("i", 20), ("n", 15), ("k", 12), ("t", 8)])
    code = (f"{var} = 0\n"
            f"while {var} < {limit}\n"
            f"   Put {var} to output\n"
            f"   {var} = {var} + 1")
    answers = {"expression": f"{var} < {limit}",
               "initialization": f"{var} = 0",
               "update": f"{var} = {var} + 1"}
    correct = answers[part]
    wrong = [v for k, v in answers.items() if k != part] + [var]
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    label = {"expression": "loop expression",
             "initialization": "loop variable initialization",
             "update": "loop variable update"}[part]
    return {"concept": "loop-anatomy", "type": "mcq",
            "prompt": f"What is the {label} in this pseudocode?\n\n{code}",
            "options": opts, "answer": idx,
            "explain": f"The {label} is  {correct}. A loop has three parts: the "
                       f"initialization (sets the starting value), the expression "
                       f"(the condition checked each pass), and the update (moves "
                       f"the variable toward the exit)."}


def g_infinite_loop(rng, ctx):
    limit = rng.choice([3, 5, 8])
    code = (f"count = 0\n"
            f"while count < {limit}\n"
            f"   Put \"Hi\" to output")
    correct = "\"Hi\" prints indefinitely"
    wrong = [f"\"Hi\" prints {limit} times",
             f"\"Hi\" prints {limit - 1} times",
             "The program throws an error"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "infinite-loop", "type": "mcq",
            "prompt": "What is the result of running this code?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"count is never incremented inside the loop body, so "
                       f"count < {limit} stays true forever — an INFINITE loop. "
                       f"Every loop body must change something that moves the "
                       f"condition toward false."}


# =========================================================================
# Ch 5 — Arrays
# =========================================================================
def g_array_indices(rng, ctx):
    n = rng.choice([5, 6, 8, 10, 12])
    correct = f"0 through {n - 1}"
    wrong = [f"1 through {n}", f"0 through {n}", f"1 through {n - 1}"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "array-index", "type": "mcq",
            "prompt": f"An array is declared to hold {n} elements. What are its "
                      f"valid indices?",
            "options": opts, "answer": idx,
            "explain": f"Array indices are 0-BASED. An array of {n} elements has "
                       f"indices 0 through {n-1}; the last valid index is "
                       f"size - 1. Index {n} is out of range."}


def g_array_last_index(rng, ctx):
    correct = "vals.size - 1"
    wrong = ["vals.size", "vals[vals.size]", "vals[0]"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "array-index", "type": "mcq",
            "prompt": "An array named vals holds an unknown number of elements. "
                      "Which EXPRESSION gives the index of the last element, for "
                      "an array of any size?",
            "options": opts, "answer": idx,
            "explain": "Indices run 0..size-1, so the last index is "
                       "vals.size - 1. Note vals.size is the COUNT (one past the "
                       "last index), and vals[...] retrieves an ELEMENT rather "
                       "than naming a position."}


def g_array_max_seed(rng, ctx):
    correct = "userVals[0], the array's first element"
    wrong = ["0", "the largest possible integer", "userVals.size"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "array-iterate", "type": "mcq",
            "prompt": "A loop finds the maximum value in an integer array "
                      "userVals. What should maxVal be initialized to before the "
                      "loop begins?",
            "options": opts, "answer": idx,
            "explain": "Seed with the FIRST ELEMENT. Seeding with 0 fails when "
                       "every value is negative: 0 would never be replaced and "
                       "would be reported as the maximum even though it is not in "
                       "the array. Starting at userVals[0] guarantees the seed is "
                       "a real element."}


def g_array_traverse(rng, ctx):
    """COMPUTED: what a flag-setting traversal reports."""
    threshold = rng.choice([0, 50, 100])
    cond = rng.choice(["<", ">"])
    if cond == "<":
        meaning = f"At least one element is less than {threshold}"
        other = [f"All elements are less than {threshold}",
                 f"No element is less than {threshold}",
                 f"Exactly one element is less than {threshold}"]
    else:
        meaning = f"At least one element is greater than {threshold}"
        other = [f"All elements are greater than {threshold}",
                 f"No element is greater than {threshold}",
                 f"Exactly one element is greater than {threshold}"]
    code = (f"i = 0\n"
            f"x = 0\n"
            f"while i < list.size\n"
            f"   if list[i] {cond} {threshold}\n"
            f"      x = 1\n"
            f"   i = i + 1\n"
            f"Put x to output")
    opts, idx = _shuffle_answer(rng, meaning, other)
    return {"concept": "array-iterate", "type": "mcq",
            "prompt": "What does an output of 1 indicate for this algorithm?\n\n"
                      + code,
            "options": opts, "answer": idx,
            "explain": f"x starts at 0 and is set to 1 the moment ANY element "
                       f"satisfies the test. It is never reset, so an output of 1 "
                       f"means AT LEAST ONE element matched — not all of them, and "
                       f"not exactly one."}


def g_array_swap(rng, ctx):
    correct = "A third, temporary variable"
    wrong = ["Nothing extra — x = y then y = x is enough",
             "An extra array element",
             "A constant"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "array-swap", "type": "mcq",
            "prompt": "What is required in order to swap the values of two "
                      "variables x and y?",
            "options": opts, "answer": idx,
            "explain": "You need a TEMP variable: temp = x; x = y; y = temp. "
                       "Without it, 'x = y' destroys x's old value before it can "
                       "be copied into y, and both end up holding y."}


# =========================================================================
# Ch 6 — Functions
# =========================================================================
def g_param_vs_arg(rng, ctx):
    fname, pname, val = rng.choice([("CircleArea", "radius", "5.0"),
                                    ("BoxVolume", "side", "3.0"),
                                    ("TaxOwed", "income", "42000.0"),
                                    ("Discount", "price", "19.99")])
    correct = f"{pname} is the parameter; {val} is the argument"
    wrong = [f"{pname} is the argument; {val} is the parameter",
             f"Both {pname} and {val} are parameters",
             f"Both {pname} and {val} are arguments"]
    code = (f"Function {fname}(float {pname}) returns float result\n"
            f"   ...\n\n"
            f"{fname}({val})")
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "param-vs-arg", "type": "mcq",
            "prompt": "Consider the definition and call below. Which correctly "
                      "identifies the parameter and the argument?\n\n" + code,
            "options": opts, "answer": idx,
            "explain": f"A PARAMETER is the variable named in the DEFINITION (a "
                       f"placeholder): {pname}. An ARGUMENT is the actual value "
                       f"supplied at the CALL: {val}. The argument is copied into "
                       f"the parameter."}


def g_func_return_compute(rng, ctx):
    """COMPUTED: evaluate a user-defined function at a value."""
    m, b, x = rng.choice([(3, 1, 4), (2, 5, 6), (4, 2, 3), (5, 3, 2), (2, 7, 5)])
    truth = m * x + b
    wrong = [str(m + x + b), str(m * (x + b)), str(x)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    code = (f"Function P(integer x) returns integer y\n"
            f"   y = (x * {m}) + {b}")
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "func-return", "type": "mcq",
            "prompt": f"{code}\n\nWhat does  P({x})  evaluate to?",
            "options": opts, "answer": idx,
            "explain": f"Substitute the argument into the parameter: y = ({x} * "
                       f"{m}) + {b} = {truth}. A function call is an EXPRESSION — "
                       f"it evaluates to its returned value."}


def g_func_output_repeat(rng, ctx):
    """COMPUTED: repeated calls concatenate output; no automatic newline/space."""
    word = rng.choice(["Go", "Hi", "Yes", "Up"])
    n = rng.choice([2, 3, 4])
    truth = word * n
    wrong = [word,
             " ".join([word] * n),
             word[0] * n + word[1:]]
    wrong = [w for w in wrong if w != truth]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, truth, 'int')
    code = f"Function G()\n   Put \"{word}\" to output"
    opts, idx = _shuffle_answer(rng, truth, wrong[:3])
    return {"concept": "func-output", "type": "mcq",
            "prompt": f"{code}\n\nWhat entire output appears after {n} successive "
                      f"calls to G()?",
            "options": opts, "answer": idx,
            "explain": f"Each call re-runs the body, and Put adds NO newline and "
                       f"NO space unless you explicitly output one. {n} calls "
                       f"therefore concatenate into {truth!r}."}


def g_func_returns_what(rng, ctx):
    inp, out = rng.choice([("n", "result"), ("x", "z"), ("value", "total")])
    correct = f"{out} only"
    wrong = [f"{inp} only", f"{inp} and {out}", "Nothing"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "func-return", "type": "mcq",
            "prompt": f"A function MyCalc has an input {inp} and an output {out}. "
                      f"What does MyCalc return?",
            "options": opts, "answer": idx,
            "explain": f"A function returns its OUTPUT: {out}. The input {inp} is "
                       f"what is passed IN (the argument copied into the "
                       f"parameter); it is not returned."}


def g_return_value_def(rng, ctx):
    correct = "The output of the function"
    wrong = ["The data passed into the function",
             "The statement that calls the function",
             "The name used in the function's definition"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "func-return", "type": "mcq",
            "prompt": "What is the return value of a function?",
            "options": opts, "answer": idx,
            "explain": "The return value is the function's OUTPUT — the value sent "
                       "back to the caller by the return statement, which also "
                       "immediately exits the function."}


def g_func_naming(rng, ctx):
    correct = "Any valid identifier"
    wrong = ["A reserved word", "Any floating-point number", "Any string literal"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "func-naming", "type": "mcq",
            "prompt": "What is a valid user-defined function name?",
            "options": opts, "answer": idx,
            "explain": "A function name follows the same rules as any identifier: "
                       "letters, digits and underscores, not starting with a "
                       "digit, and not a reserved word."}


def g_modular_incremental(rng, ctx):
    which = rng.choice(["modular", "incremental"])
    defs = {"modular": "Dividing a program into separate functions that can be "
                       "developed and tested independently, then integrated",
            "incremental": "Writing and testing a small amount of code, then "
                           "adding a little more and testing again"}
    correct = defs[which]
    wrong = [defs["incremental" if which == "modular" else "modular"],
             "Converting a program from an interpreted language to a compiled one",
             "Replacing every variable with a constant"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "modular-dev", "type": "mcq",
            "prompt": f"What is {which} development?",
            "options": opts, "answer": idx,
            "explain": f"{which.capitalize()} development: {correct.lower()}. "
                       f"Functions exist to improve readability, enable reuse, and "
                       f"make a program testable in pieces."}


# =========================================================================
# Ch 7 — Algorithms
# =========================================================================
def g_algorithm_text(rng, ctx):
    algos = ["Preheat the oven; mix the batter; bake for 30 minutes.",
             "Insert the key; turn the key; open the door.",
             "Shake the bulb; if it rattles, replace it.",
             "Take one card; place it in sorted position; repeat until none remain."]
    facts = ["The sky is blue and the grass is green.",
             "A car has four wheels.",
             "Water is wet; fire is not wet.",
             "The maximum speed is 60 mph.",
             "Tuesday follows Monday."]
    correct = rng.choice(algos)
    rng.shuffle(facts)
    opts, idx = _shuffle_answer(rng, correct, facts[:3])
    return {"concept": "algorithm-def", "type": "mcq",
            "prompt": "Which text represents an ALGORITHM?",
            "options": opts, "answer": idx,
            "explain": "An algorithm is a SEQUENCE OF STEPS that solves a problem. "
                       "The other options are statements of fact — they describe "
                       "something, but they do not tell you what to DO, in order."}


def g_algorithm_when(rng, ctx):
    correct = "Before writing a program to solve the problem"
    wrong = ["Before knowing the problem",
             "While writing a program to solve the problem",
             "After writing a program to solve the problem"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "algorithm-def", "type": "mcq",
            "prompt": "When should a programmer develop an algorithm to solve a "
                      "problem?",
            "options": opts, "answer": idx,
            "explain": "The algorithm comes FIRST — you design a correct sequence "
                       "of steps, then translate it into code. Coding without an "
                       "algorithm is how you get a program that works on one input "
                       "and fails on the rest."}


def g_comp_problem(rng, ctx):
    """Section 7.2 — the input/question/output triple."""
    asked = rng.choice(["parts", "example"])
    if asked == "parts":
        correct = "An input, a question about the input, and the desired output"
        wrong = ["A programming language, a compiler, and an interpreter",
                 "An algorithm, a flowchart, and pseudocode",
                 "A hypothesis, a test, and a result"]
        prompt = "A computational problem specifies which three things?"
    else:
        correct = ("Input: a list of integers. Question: what is the largest "
                   "value? Output: the largest integer.")
        wrong = ["Input: a compiler. Question: is it fast? Output: machine code.",
                 "Input: a flowchart. Question: is it correct? Output: a program.",
                 "Input: a bug. Question: where is it? Output: a hypothesis."]
        prompt = "Which correctly states a computational problem?"
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "comp-problem", "type": "mcq",
            "prompt": prompt, "options": opts, "answer": idx,
            "explain": "A computational problem specifies an INPUT, a QUESTION "
                       "about that input that a computer can answer, and the "
                       "desired OUTPUT. An algorithm is then the sequence of steps "
                       "that solves it — and one problem may have many possible "
                       "algorithms."}


def g_efficiency_case(rng, ctx):
    which = rng.choice(["best", "worst"])
    defs = {"best": "The scenario in which the algorithm does the fewest possible "
                    "operations",
            "worst": "The scenario in which the algorithm does the most possible "
                     "operations"}
    correct = defs[which]
    wrong = [defs["worst" if which == "best" else "best"],
             "The scenario in which the algorithm uses the least memory",
             "The average of all possible scenarios"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "algo-efficiency", "type": "mcq",
            "prompt": f"What is an algorithm's {which.upper()} case?",
            "options": opts, "answer": idx,
            "explain": f"{which.capitalize()} case = {correct.lower()}. Efficiency "
                       f"is measured in runtime (operations) and memory; the WORST "
                       f"case is the one to analyze when you need a guarantee."}


def g_efficiency_polynomial(rng, ctx):
    truth = rng.choice([True, False])
    stmt = ("An algorithm with a polynomial runtime is considered efficient."
            if truth else
            "An algorithm's efficiency is measured only by how much memory it "
            "uses, never by its runtime.")
    return {"concept": "algo-efficiency", "type": "tf",
            "prompt": stmt, "answer": truth,
            "explain": "Efficiency covers BOTH runtime (number of operations) and "
                       "memory. Polynomial runtime is considered efficient; "
                       "exponential runtime is not."}


def g_linear_search(rng, ctx):
    """COMPUTED: worst case = N."""
    n = rng.choice([12, 20, 50, 64, 100, 250])
    truth = str(n)
    wrong = [str(n // 2), "1", str(max(1, n.bit_length() - 1))]
    wrong = [w for w in wrong if w != truth]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, truth, 'int')
    opts, idx = _shuffle_answer(rng, truth, wrong[:3])
    return {"concept": "search-linear", "type": "mcq",
            "prompt": f"A list holds {n} elements. In the WORST case, how many "
                      f"elements does a linear search examine?",
            "options": opts, "answer": idx,
            "explain": f"Linear search checks elements one at a time from the "
                       f"start. The worst case is the key being last or absent, so "
                       f"it examines all {n}. Linear search works on ANY list — "
                       f"sorted or not."}


def g_binary_search_steps(rng, ctx):
    """COMPUTED: worst case ~ log2(N)."""
    n = rng.choice([16, 32, 64, 128, 256, 1024])
    truth = n.bit_length() - 1               # exact log2 for powers of two
    wrong = [str(n), str(n // 2), str(truth * 2)]
    wrong = [w for w in wrong if w != str(truth)]
    wrong = [w for w in wrong][:3]
    wrong = _pad(wrong, str(truth), 'int')
    opts, idx = _shuffle_answer(rng, str(truth), wrong[:3])
    return {"concept": "search-binary", "type": "mcq",
            "prompt": f"A SORTED array holds {n} elements. In the worst case, "
                      f"roughly how many elements does a BINARY search examine?",
            "options": opts, "answer": idx,
            "explain": f"Binary search checks the middle element and discards half "
                       f"the remaining elements each step: log2({n}) = {truth}. "
                       f"Linear search would need up to {n}. Each doubling of the "
                       f"list adds only ONE extra comparison."}


def g_binary_search_requires(rng, ctx):
    correct = "The list must be sorted and directly accessible (like an array)"
    wrong = ["The list must be unsorted",
             "The list must contain only positive numbers",
             "The list must have an even number of elements"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "search-binary", "type": "mcq",
            "prompt": "What does binary search REQUIRE of the list it searches?",
            "options": opts, "answer": idx,
            "explain": "Binary search discards half the list based on how the "
                       "middle element compares to the key — which only works if "
                       "the list is SORTED and you can jump to the middle. On an "
                       "unsorted list it gives wrong answers."}


def g_sorting(rng, ctx):
    correct = "Repeatedly swapping elements that are out of order"
    wrong = ["Discarding half the list on each comparison",
             "Checking each element one at a time until a key is found",
             "Grouping data and operations into a single object"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "sorting", "type": "mcq",
            "prompt": "Sorting arranges a list's elements in order. Which "
                      "describes a common way to accomplish it?",
            "options": opts, "answer": idx,
            "explain": "A basic sort repeatedly SWAPS out-of-order pairs until the "
                       "list is ordered. (Discarding half per comparison describes "
                       "binary SEARCH, not a sort.)"}


def g_algo_ordering(rng, ctx):
    """Ordering as MCQ. Every sequence must assemble into a RUNNABLE program:
    no variable is used before it is assigned."""
    task = rng.choice([
        ("output the maximum of x and y",
         ["Declare variable max", "max = x", "If y > max, set max = y",
          "Put max to output"]),
        ("output each diner's share of a bill, given totalBill and numDiners",
         ["Declare variable share", "share = totalBill / numDiners",
          "Put share to output", "End the program"]),
        ("output the average of a and b",
         ["Declare variable avg", "avg = (a + b) / 2.0", "Put avg to output",
          "End the program"]),
    ])
    what, steps = task
    correct = " → ".join(steps)
    # distractors: plausible but broken orders (use-before-assign / output-first)
    w1 = " → ".join([steps[1], steps[0]] + steps[2:])       # use before declare
    w2 = " → ".join([steps[-1] if len(steps) > 3 else steps[2]] + steps[:-1])
    w3 = " → ".join(list(reversed(steps)))
    wrong = [w for w in dict.fromkeys([w1, w2, w3]) if w != correct][:3]
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "algo-ordering", "type": "mcq",
            "prompt": f"Which is the correct order of statements to {what}?",
            "options": opts, "answer": idx,
            "explain": f"Correct order: {correct}. The shape is always DECLARE → "
                       f"COMPUTE → OUTPUT. Test any ordering by assembling it and "
                       f"executing it mentally: if a variable is used before it "
                       f"holds a value, the order is wrong."}


def g_algo_valid_test(rng, ctx):
    correct = "Input 9, 0, 4. Ensure the output is \"INVALID.\""
    wrong = ["Input 9, 2, 4. Ensure the output is \"INVALID.\"",
             "Input 9, 0, 4. Ensure the output is \"VALID.\"",
             "Input 0, 0, 0. Ensure the output is \"VALID.\""]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "algorithm-def", "type": "mcq",
            "prompt": "An algorithm should output \"VALID\" if every number in a "
                      "list is non-zero, and \"INVALID\" otherwise.\nWhich is a "
                      "VALID test of the algorithm?",
            "options": opts, "answer": idx,
            "explain": "A test must pair an input with the output the SPEC "
                       "requires. The list 9, 0, 4 contains a zero, so a correct "
                       "algorithm must output \"INVALID\" — that pairing is the "
                       "only one that actually checks the rule."}


# =========================================================================
# Ch 8 — The design process (SDLC, objects, UML). 21% of the exam.
# =========================================================================
PHASES = ["Analysis", "Design", "Implementation", "Testing"]

_PHASE_JOB = {
    "Analysis":       "defines the program's GOALS (what to build)",
    "Design":         "defines HOW the program will be built (specifics, "
                      "components, diagrams)",
    "Implementation": "WRITES the program (code)",
    "Testing":        "checks that the program correctly MEETS the goals",
}


def g_sdlc_phase_job(rng, ctx):
    phase = rng.choice(PHASES)
    correct = _PHASE_JOB[phase]
    wrong = [v for k, v in _PHASE_JOB.items() if k != phase]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "sdlc-phases", "type": "mcq",
            "prompt": f"In the systems development life cycle, what does the "
                      f"{phase.upper()} phase do?",
            "options": opts, "answer": idx,
            "explain": f"{phase} {correct}. The four phases in order: Analysis "
                       f"(goals) → Design (how) → Implementation (write it) → "
                       f"Testing (does it meet the goals?)."}


def g_sdlc_scenario(rng, ctx):
    """THE archetype WGU loves: the stem narrates several phases, then asks about
    ONE. Every distractor is pre-loaded into the setup. Trains the habit of
    reading the FINAL sentence first."""
    scenarios = [
        # (setup narrating other phases, the thing actually asked, correct phase)
        ("A team decides a program should track library book loans, and then "
         "decides to build it in Java using several classes.",
         "the programmer opens an editor and begins typing code", "Implementation"),
        ("A programmer has finished writing a payroll program and handed it off.",
         "a colleague runs it on 500 different inputs, checking each output is "
         "correct", "Testing"),
        ("A programmer shows the first version of a scheduling app to a client.",
         "the client's feedback causes the program's GOALS to be redefined",
         "Analysis"),
        ("Leadership has agreed the company needs a customer-tracking system and "
         "has approved the budget.",
         "the team produces the list of classes and components the system will "
         "need", "Design"),
        ("A programmer has already coded and shipped version one of a game.",
         "the programmer begins writing version two based on player feedback",
         "Implementation"),
        ("A team has gathered requirements and drawn the class diagrams.",
         "a tester confirms the outputs occur in the expected order for given "
         "inputs", "Testing"),
        ("A company has an existing inventory program written last year.",
         "management determines the new system must support barcode scanning as "
         "well as manual entry", "Analysis"),
    ]
    setup, asked, correct = rng.choice(scenarios)
    wrong = [p for p in PHASES if p != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "sdlc-scenario", "type": "mcq",
            "prompt": f"{setup}\n\nWhich phase is occurring when {asked}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. Read the FINAL question sentence first — the "
                       f"setup deliberately narrates OTHER phases to bait you. "
                       f"Map the key words: goals/requirements → Analysis; "
                       f"how/components/diagrams → Design; writing code → "
                       f"Implementation; running & checking outputs → Testing."}


def g_sdlc_goals(rng, ctx):
    approach = rng.choice(["a waterfall", "an agile"])
    correct = "Analysis"
    wrong = ["Design", "Implementation", "Testing"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "sdlc-scenario", "type": "mcq",
            "prompt": f"In {approach} approach, in which phase are a program's "
                      f"GOALS defined or changed?",
            "options": opts, "answer": idx,
            "explain": "GOALS always belong to ANALYSIS — in waterfall and in "
                       "agile alike. Agile simply loops back to analysis when "
                       "customer feedback changes what the program should do."}


def g_objects(rng, ctx):
    correct = "A grouping of data (variables) and the operations (functions) "\
              "performed on that data"
    wrong = ["A single variable that holds exactly one value",
             "A diagram showing a program's control flow",
             "A list of the program's goals"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "objects", "type": "mcq",
            "prompt": "In programming, what is an object?",
            "options": opts, "answer": idx,
            "explain": "An object bundles DATA and the OPERATIONS on that data "
                       "into one higher-level unit, letting large programs be "
                       "organized around real-world things rather than loose "
                       "variables and functions."}


_UML = {
    "Use case diagram": "Provides an overview of several use cases — what users "
                        "can do with the system",
    "Class diagram":    "Depicts a class's name, data members, and functions",
    "Activity diagram": "Describes the flow of the program's actions, including "
                        "its branches and loops",
    "Sequence diagram": "Shows the order of events/messages between components "
                        "over time",
}


def g_uml_purpose(rng, ctx):
    name = rng.choice(list(_UML))
    correct = _UML[name]
    wrong = [v for k, v in _UML.items() if k != name]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "uml-diagrams", "type": "mcq",
            "prompt": f"What is the purpose of a {name.upper()}?",
            "options": opts, "answer": idx,
            "explain": f"{name}: {correct}. Keep the confusable pair straight — "
                       f"ACTIVITY shows the flow of actions INSIDE the program "
                       f"(branches and loops); SEQUENCE shows the order of events "
                       f"BETWEEN components."}


def g_uml_from_description(rng, ctx):
    desc = rng.choice([
        ("describes the flow of a program's actions, including branches and loops",
         "Activity diagram"),
        ("shows the order of messages exchanged between program components over "
         "time", "Sequence diagram"),
        ("shows a class's name, its data members, and its functions",
         "Class diagram"),
        ("gives an overview of several use cases and the actors who perform them",
         "Use case diagram"),
    ])
    what, correct = desc
    wrong = [k for k in _UML if k != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "uml-diagrams", "type": "mcq",
            "prompt": f"Which UML diagram {what}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. Tells: 'branches and loops' or 'the program's "
                       f"instructions' → ACTIVITY. 'Between components' or 'order "
                       f"of events' → SEQUENCE. 'Data members and functions' → "
                       f"CLASS. 'Several use cases / what a user can do' → USE "
                       f"CASE."}


def g_uml_structural_behavioral(rng, ctx):
    kind = rng.choice(["structural", "behavioral"])
    if kind == "structural":
        correct = "Class diagram"
        wrong = ["Activity diagram", "Sequence diagram", "Use case diagram"]
    else:
        correct = rng.choice(["Sequence diagram", "Activity diagram"])
        wrong = ["Class diagram"] + [d for d in ["Sequence diagram",
                                                 "Activity diagram",
                                                 "Use case diagram"]
                                     if d != correct][:2]
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "uml-diagrams", "type": "mcq",
            "prompt": f"Which of these is a {kind.upper()} UML diagram?",
            "options": opts, "answer": idx,
            "explain": f"A CLASS diagram is STRUCTURAL — it shows what the system "
                       f"is made of. Activity and sequence diagrams are "
                       f"BEHAVIORAL — they show what the system does over time."}


def g_uml_phase(rng, ctx):
    """Where a diagram is CREATED. Note: the course text describes sequence
    diagrams being USED during testing, but the exam asks where they are CREATED,
    which is DESIGN. Both facts are taught; the exam rewards the design answer."""
    cases = [
        ("a use case diagram capturing what users need the system to do",
         "Analysis"),
        ("a sequence diagram specifying the required order of events between "
         "program components", "Design"),
        ("a class diagram laying out the classes the program will be built from",
         "Design"),
    ]
    what, correct = rng.choice(cases)
    wrong = [p for p in PHASES if p != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "uml-phase-map", "type": "mcq",
            "prompt": f"Which phase of a waterfall approach would CREATE {what}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. Use case diagrams capture GOALS, so they "
                       f"belong to Analysis. The other diagrams describe HOW the "
                       f"program will be built, so they are created during DESIGN "
                       f"— even though a sequence diagram is later USED in Testing "
                       f"to verify event order. 'Created in' and 'used in' are "
                       f"different questions."}


def g_waterfall_agile(rng, ctx):
    facts = [
        ("In which approach is the implementation phase carried out many separate "
         "times?", "Agile"),
        ("In which approach are the phases carried out once, in sequence?",
         "Waterfall"),
        ("Which approach adapts most easily to changing customer requirements?",
         "Agile"),
        ("In which approach would a single phase, such as implementation, likely "
         "take the longest?", "Waterfall"),
    ]
    q, correct = rng.choice(facts)
    wrong = ["Waterfall" if correct == "Agile" else "Agile", "Neither",
             "Both equally"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "waterfall-agile", "type": "mcq",
            "prompt": q, "options": opts, "answer": idx,
            "explain": f"{correct}. WATERFALL runs the four phases once, in order, "
                       f"with each phase potentially long and late change costly. "
                       f"AGILE repeats short cycles, so implementation (and every "
                       f"other phase) happens many times."}


def g_agile_versions(rng, ctx):
    n = rng.choice(["second", "third", "fourth", "fifth"])
    correct = "Implementation"
    wrong = ["Analysis", "Design", "Testing"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "sdlc-scenario", "type": "mcq",
            "prompt": f"A programmer is writing the {n} version of a program, each "
                      f"version adding features customers asked for.\nIn which "
                      f"phase of an agile approach does WRITING that version occur?",
            "options": opts, "answer": idx,
            "explain": "Writing code is IMPLEMENTATION, no matter which iteration "
                       "you are on. Agile repeats the phases; it does not rename "
                       "them."}


# =========================================================================
# Ch 9 — Languages & libraries (18% of the exam)
# =========================================================================
def g_compiled_interpreted(rng, ctx):
    which = rng.choice(["compiled", "interpreted"])
    if which == "compiled":
        correct = "It is converted to machine language before running"
        wrong = ["It runs one statement at a time by way of another program",
                 "It runs on any machine that has an interpreter",
                 "It is generally slower than an interpreted language"]
    else:
        correct = "It runs easily on different kinds of machines"
        wrong = ["It must be converted to machine code before running",
                 "It generally runs faster than a compiled language",
                 "It produces a standalone executable file"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "compiled-interp", "type": "mcq",
            "prompt": f"What is a characteristic of {'an' if which[0] in 'aeiou' else 'a'} "
                      f"{which.upper()} language?",
            "options": opts, "answer": idx,
            "explain": "COMPILED: a compiler converts the whole program to machine "
                       "code first; it runs faster but the build is machine-"
                       "specific (C, C++, Java). INTERPRETED (scripting): an "
                       "interpreter runs it one statement at a time; slower, but "
                       "portable and modifiable at run time (Python, JavaScript)."}


def g_interpreted_advantage(rng, ctx):
    correct = "They can be modified at run time"
    wrong = ["They generally run faster than compiled programs",
             "They always use memory more efficiently",
             "They compile to machine code automatically"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "compiled-interp", "type": "mcq",
            "prompt": "What is an advantage of interpreted programs?",
            "options": opts, "answer": idx,
            "explain": "Because an interpreter executes statements one at a time, "
                       "an interpreted program can be modified AT RUN TIME, and it "
                       "runs on any machine with the right interpreter. What it is "
                       "NOT is faster — compiled code wins on speed."}


def g_typing(rng, ctx):
    which = rng.choice(["statically", "dynamically"])
    if which == "statically":
        correct = "A variable's type is fixed and checked before the program runs"
        example = "C, C++ and Java are statically typed"
    else:
        correct = "A variable's type can change while the program is running"
        example = "Python is dynamically typed"
    wrong = [("A variable's type can change while the program is running"
              if which == "statically" else
              "A variable's type is fixed and checked before the program runs"),
             "Variables have no type at all",
             "Every variable must be a constant"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "typing", "type": "mcq",
            "prompt": f"What does it mean for a language to be {which.upper()} "
                      f"typed?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. {example}. A programmer who wants the COMPILER "
                       f"to catch a bad assignment (e.g. a string into an integer) "
                       f"needs a STATICALLY typed language."}


def g_typing_which_language(rng, ctx):
    ask = rng.choice(["dynamically typed", "NOT object-oriented"])
    if ask == "dynamically typed":
        correct, wrong = "Python", ["C", "C++", "Java"]
    else:
        correct, wrong = "C", ["C++", "Java", "Python"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "typing" if ask == "dynamically typed" else "lang-kinds",
            "type": "mcq",
            "prompt": f"Which language is {ask}?",
            "options": opts, "answer": idx,
            "explain": ("Python is dynamically typed — a variable's type can "
                        "change at run time. C, C++ and Java are statically typed."
                        if ask == "dynamically typed" else
                        "C is not built on object-oriented design principles. C++, "
                        "Java and Python all provide substantial support for "
                        "objects.")}


def g_lang_kind(rng, ctx):
    cases = [
        ("uses tags surrounding text to describe how that text should be "
         "displayed", "Markup"),
        ("substantially supports creating items like person, teacher and student, "
         "each holding internal data and operations", "Object-oriented"),
        ("has a compiler that reports an error if a float variable is assigned a "
         "string", "Statically typed"),
        ("lets a variable hold a string and later hold an integer, while running",
         "Dynamically typed"),
    ]
    what, correct = rng.choice(cases)
    wrong = [c for _, c in cases if c != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "lang-kinds", "type": "mcq",
            "prompt": f"A language {what}.\nWhich characteristic describes it?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. Note these kinds are NOT mutually exclusive — "
                       f"a language can be object-oriented AND dynamically typed "
                       f"(Python is both). HTML is the classic MARKUP language: it "
                       f"describes structure and formatting rather than computing."}


def g_library_first_step(rng, ctx):
    correct = "Include the library"
    wrong = ["Write the library's functions",
             "Modify the library's functions",
             "Compile the library from scratch"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "libraries", "type": "mcq",
            "prompt": "What does a programmer do FIRST to use an existing "
                      "programming library?",
            "options": opts, "answer": idx,
            "explain": "You INCLUDE the library — that is the whole point: the "
                       "functions are already written and already tested, so you "
                       "reuse them rather than rewriting them."}


def g_library_facts(rng, ctx):
    facts = [
        ("What is an advantage of using a programming library?",
         "The code has already been tested",
         ["The code has not yet been tested",
          "The code runs without an interpreter on any machine",
          "The code never needs to be included"]),
        ("What relationship is common among a programming library's functions?",
         "The functions all relate to the same purpose",
         ["Each function competes with the others",
          "Each function fixes bugs in the other functions",
          "Every function performs the identical computation"]),
        ("What is a programming library?",
         "A set of pre-written functions that carry out common tasks",
         ["A diagram of a program's classes",
          "A language that uses tags to format text",
          "The list of a program's goals"]),
    ]
    q, correct, wrong = rng.choice(facts)
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "libraries", "type": "mcq",
            "prompt": q, "options": opts, "answer": idx,
            "explain": "A library is a set of PRE-WRITTEN, already-TESTED "
                       "functions that all serve a common purpose (math, "
                       "statistics, graphics). Libraries improve productivity "
                       "because you reuse proven code instead of writing it."}


# =========================================================================
# Ch 10 — Troubleshooting
# =========================================================================
def g_hypothesis_test(rng, ctx):
    term = rng.choice(["hypothesis", "test"])
    defs = {"hypothesis": "A proposed cause of the problem",
            "test": "A procedure whose result validates or invalidates a "
                    "proposed cause"}
    correct = defs[term]
    wrong = [defs["test" if term == "hypothesis" else "hypothesis"],
             "A permanent fix for the underlying defect",
             "A written record of the problem for a future programmer"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "troubleshoot", "type": "mcq",
            "prompt": f"In troubleshooting, what is a {term.upper()}?",
            "options": opts, "answer": idx,
            "explain": f"A {term} is {correct.lower()}. The cycle is: form a "
                       f"HYPOTHESIS (proposed cause) → run a TEST → the test either "
                       f"VALIDATES it (cause found) or INVALIDATES it (move to the "
                       f"next hypothesis). A test that can do neither is useless."}


def g_test_outcome(rng, ctx):
    truth = rng.choice([True, False])
    stmt = ("A good test should either validate or invalidate a hypothesis."
            if truth else
            "Troubleshooting means trying random fixes until the problem goes "
            "away.")
    return {"concept": "troubleshoot", "type": "tf",
            "prompt": stmt, "answer": truth,
            "explain": "Troubleshooting is a SYSTEMATIC process. A useful test "
                       "must be able to validate or invalidate the hypothesis; "
                       "random changes are the opposite of the method."}


def g_hypothesis_order(rng, ctx):
    correct = "The most likely and most easily-testable hypotheses first"
    wrong = ["The least likely hypotheses first",
             "The hypotheses that take the longest to test first",
             "Hypotheses in alphabetical order"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "hypothesis-order", "type": "mcq",
            "prompt": "When several hypotheses could explain a problem, which "
                      "should be tested first?",
            "options": opts, "answer": idx,
            "explain": "Test the most LIKELY and most EASILY TESTABLE hypotheses "
                       "first — that finds the cause fastest. Hypotheses can also "
                       "be arranged HIERARCHICALLY, starting broad and narrowing to "
                       "a specific cause."}


def g_asymmetric_test(rng, ctx):
    correct = "A test that gives a more conclusive result on one outcome than "\
              "the other"
    wrong = ["A test that always validates the hypothesis",
             "A test that can never invalidate a hypothesis",
             "A test performed by two people at once"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "hypothesis-order", "type": "mcq",
            "prompt": "What is an asymmetric test?",
            "options": opts, "answer": idx,
            "explain": "An asymmetric test is more conclusive one way than the "
                       "other. Plugging a lamp into a known-good outlet is one: if "
                       "it works, 'the lamp is broken' is conclusively invalidated; "
                       "if it doesn't, the result is less certain."}


# =========================================================================
# Ch 11 — Debugging
# =========================================================================
def g_debug_output(rng, ctx):
    correct = "To reveal the actual values of variables so they can be compared "\
              "to the expected values"
    wrong = ["To make the program run faster",
             "To permanently document the program's logic",
             "To convert the program from interpreted to compiled"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "debug-output", "type": "mcq",
            "prompt": "Why does a programmer insert temporary debug output "
                      "statements while debugging?",
            "options": opts, "answer": idx,
            "explain": "Debug output prints what the program is ACTUALLY doing so "
                       "you can compare it against what you EXPECTED. Once the "
                       "cause is found, remove the statements so they don't "
                       "clutter real output."}


def g_debug_binary(rng, ctx):
    correct = "Binary search of the code"
    wrong = ["Incremental development", "Type casting", "Modular development"]
    opts, idx = _shuffle_answer(rng, correct, wrong)
    return {"concept": "debug-output", "type": "mcq",
            "prompt": "A long program produces a wrong result. The programmer "
                      "checks whether the bug is in the first half or the second "
                      "half, discards the correct half, and repeats.\nWhich "
                      "technique is this?",
            "options": opts, "answer": idx,
            "explain": "Halving the search space each step is a BINARY SEARCH — "
                       "the same halving idea used to search a sorted array, "
                       "applied to locating a fault in code."}


def g_bug_type(rng, ctx):
    cases = [
        ("a program computes 132 instead of 212 because 9 / 5 truncated to 1",
         "Calculation error"),
        ("a program gives the wrong discount because the condition tests > "
         "instead of >=", "Logic error"),
        ("a program's loop runs one time too many, producing an extra output",
         "Loop error"),
        ("a function is called with its two arguments in the wrong order",
         "Function error"),
    ]
    what, correct = rng.choice(cases)
    wrong = [c for _, c in cases if c != correct]
    rng.shuffle(wrong)
    opts, idx = _shuffle_answer(rng, correct, wrong[:3])
    return {"concept": "bug-types", "type": "mcq",
            "prompt": f"Which kind of bug is it when {what}?",
            "options": opts, "answer": idx,
            "explain": f"{correct}. The common categories: CALCULATION (wrong "
                       f"arithmetic/formula), LOGIC (wrong condition or branch), "
                       f"LOOP (off-by-one, wrong bounds, never terminates), and "
                       f"FUNCTION (bad parameters, return, or call)."}


def g_debug_is_troubleshooting(rng, ctx):
    truth = rng.choice([True, False])
    stmt = ("Debugging applies the troubleshooting cycle — hypothesis, test, "
            "validate or invalidate — to code."
            if truth else
            "Debug output statements should be left in the finished program so "
            "users can see the variable values.")
    return {"concept": "bug-types", "type": "tf",
            "prompt": stmt, "answer": truth,
            "explain": "Debugging IS troubleshooting applied to code: hypothesize "
                       "the faulty statement, test it (often with a debug print), "
                       "validate or invalidate, repeat. Temporary debug statements "
                       "are REMOVED once the bug is found."}


MCQ_GENERATORS = [
    # Ch 1
    g_bits_binary, g_ascii_unicode, g_flowchart_shape, g_pseudocode_def,
    g_comments_ws,
    # Ch 2
    g_int_division, g_mixed_division, g_modulo, g_modulo_use, g_precedence,
    g_math_function, g_identifier_valid, g_identifier_rule, g_data_type,
    g_constants, g_constant_vs_cast, g_variables_assign, g_divide_by_zero,
    # Ch 3
    g_branch_choice, g_relational_op, g_assignment_vs_equality, g_range_condition,
    g_logical_op, g_order_eval, g_paren_purpose, g_float_compare,
    # Ch 4
    g_loop_choice, g_do_while_trace, g_while_trace, g_for_sum, g_nested_loops,
    g_loop_anatomy, g_infinite_loop,
    # Ch 5
    g_array_indices, g_array_last_index, g_array_max_seed, g_array_traverse,
    g_array_swap,
    # Ch 6
    g_param_vs_arg, g_func_return_compute, g_func_output_repeat,
    g_func_returns_what, g_return_value_def, g_func_naming, g_modular_incremental,
    # Ch 7
    g_algorithm_text, g_algorithm_when, g_comp_problem, g_efficiency_case,
    g_efficiency_polynomial, g_linear_search, g_binary_search_steps,
    g_binary_search_requires, g_sorting, g_algo_ordering, g_algo_valid_test,
    # Ch 8
    g_sdlc_phase_job, g_sdlc_scenario, g_sdlc_goals, g_objects, g_uml_purpose,
    g_uml_from_description, g_uml_structural_behavioral, g_uml_phase,
    g_waterfall_agile, g_agile_versions,
    # Ch 9
    g_compiled_interpreted, g_interpreted_advantage, g_typing,
    g_typing_which_language, g_lang_kind, g_library_first_step, g_library_facts,
    # Ch 10
    g_hypothesis_test, g_test_outcome, g_hypothesis_order, g_asymmetric_test,
    # Ch 11
    g_debug_output, g_debug_binary, g_bug_type, g_debug_is_troubleshooting,
]

SQL_GENERATORS = []          # D278 is not a database course — no playground
