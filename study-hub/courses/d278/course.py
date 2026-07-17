"""D278 — Scripting and Programming Foundations (WGU).

OA course, Programming tier: MCQ/TF including computed code-output questions.
No SQL playground (the hub hides those tabs automatically when SAMPLE_DBS is
absent). Course language is CORAL, not C++ — see content.py.
"""
COURSE = {
    "code": "D278",
    "slug": "d278",
    "name": "Scripting and Programming \u2014 Foundations",
    "blurb": "Coral, not C++ \u2014 with a real Coral interpreter to run it in. "
             "Drills weighted from your pre-assessment: chapters 8 and 9 alone "
             "are 39% of them, because that is where the exam lives.",
    "status": "active",
    "badge": "OA BLUEPRINT \u00b7 70-ITEM PRE-ASSESSMENT",
    "unit_label": "Chapter",
    "chapter_names": {
        1:  "Introduction to Programming",
        2:  "Variables and Assignments",
        3:  "Branches",
        4:  "Loops",
        5:  "Arrays",
        6:  "User-Defined Functions",
        7:  "Algorithms",
        8:  "The Design Process (SDLC, UML)",
        9:  "Software Languages and Libraries",
        10: "Troubleshooting",
        11: "Debugging",
    },
    "topics": [
        ("division",  "Integer vs float division"),
        ("loop",      "Loops and tracing"),
        ("array",     "Arrays"),
        ("func",      "Functions"),
        ("search",    "Searching algorithms"),
        ("sdlc",      "SDLC phases"),
        ("uml",       "UML diagrams"),
        ("waterfall", "Waterfall vs agile"),
        ("lang",      "Languages and typing"),
        ("librar",    "Libraries"),
        ("debug",     "Debugging"),
        ("troublesh", "Troubleshooting"),
    ],
}
from .content import CONCEPTS, CH_WEIGHT, MCQ_GENERATORS, SQL_GENERATORS
from .playground import CoralPlayground

# Mandatory stipulation (harness-enforced). D278 teaches Coral, so it gets a
# real Coral interpreter — in-pack, because only this course uses it.
PLAYGROUND = CoralPlayground()
