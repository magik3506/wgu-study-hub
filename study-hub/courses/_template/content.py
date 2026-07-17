"""Template content. Three things every pack defines:
1. CONCEPTS   — one entry per testable idea, keyed to the course's own
                section refs (these drive tags, mastery, and weighting).
2. CH_WEIGHT  — blueprint weights per chapter, derived from the course's
                practice test. MUST sum to 1.0.
3. Generators — functions (rng, ctx) -> question dict. Prefer COMPUTED
                questions (answers derived at runtime) over static ones.
                Never mirror practice-test items; re-test the concept
                through a new surface.
MCQ dict:  {"concept", "type": "mcq", "prompt", "options", "answer": idx,
            "explain"}   (or type "tf" with a bool answer)
SQL dict:  {"concept", "type": "sql", "kind": "select|dml|ddl", "db",
            "prompt", "reference", "hint"?, plus kind-specific fields —
            copy patterns from courses/d426/content.py}
"""
CONCEPTS = {
    "example-idea": {"ch": 1, "ref": "1.1", "name": "Example idea"},
    "second-idea":  {"ch": 2, "ref": "2.1", "name": "Second idea"},
    "code-trace":   {"ch": 2, "ref": "2.2", "name": "Tracing loop output"},
}
CH_WEIGHT = {1: 0.5, 2: 0.5}

def g_example(rng, ctx):
    a, b = rng.choice([(2, 3), (4, 5), (6, 7)])
    return {"concept": "example-idea", "type": "mcq",
            "prompt": f"What is {a} + {b}?  (computed example \u2014 the "
                      "answer is derived, not stored)",
            "options": [str(a + b), str(a + b + 2), str(a * b)],
            "answer": 0,
            "explain": f"{a} + {b} = {a + b}. Computed questions never go "
                       "stale and can't be memorized."}

def g_second(rng, ctx):
    truth = rng.choice([True, False])
    return {"concept": "second-idea", "type": "tf",
            "prompt": "This template statement is "
                      + ("true." if truth else "false."),
            "answer": truth,
            "explain": "TF questions need a bool answer and an explanation."}

def g_code_output(rng, ctx):
    """ARCHETYPE: code-output prediction — for Java / Python / scripting /
    C courses where the hub can't run the language. The generator MIRRORS
    the snippet's logic in plain Python, so the correct answer is COMPUTED,
    never hard-coded, and distractors are the classic mistakes. Only use
    constructs whose semantics match simple Python ints (no overflow, no
    float division surprises), and vet every parameter triple."""
    start, step, n = rng.choice([(1, 2, 3), (1, 3, 4), (2, 2, 4)])
    total, v = 0, start
    for _ in range(n):
        total += v
        v += step
    off_by_one = total - (v - step)      # loop body ran once too few
    wrong_init = total - start           # forgot the first term
    snippet = (f"int total = 0;\nint v = {start};\n"
               f"for (int i = 0; i < {n}; i++) {{\n"
               f"    total += v;\n    v += {step};\n}}\n"
               "System.out.println(total);")
    return {"concept": "code-trace", "type": "mcq",
            "prompt": "What does this Java snippet print?\n\n" + snippet,
            "options": [str(total), str(off_by_one), str(wrong_init)],
            "answer": 0,
            "explain": f"v takes {n} values starting at {start} stepping by "
                       f"{step}; their sum is {total}. Tracing one iteration "
                       "at a time beats pattern-guessing."}

MCQ_GENERATORS = [g_example, g_second, g_code_output]
SQL_GENERATORS = []      # concept-only courses leave this empty
