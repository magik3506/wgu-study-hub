"""COURSE PACK TEMPLATE — copy this folder to courses/<slug>/ and fill in.
The harness (--selftest <slug>) must pass before a pack ships.
See courses/d426/ for a full SQL-course example, and
skills/course-pack-creator/SKILL.md for the complete pipeline."""
COURSE = {
    "code": "D000",
    "slug": "_template",
    "name": "Template Course \u2014 Copy Me",
    "blurb": "A minimal, harness-passing pack showing the contract.",
    "status": "template",          # set to "active" when real
    "badge": "ADAPTIVE DRILLS",
    "chapter_names": {1: "First chapter", 2: "Second chapter"},
    "unit_label": "Chapter",   # or "Unit" / "Module" / "Lesson" / "Section" — whatever the course calls its top-level pieces
    "topics": [("example", "Example topic")],
}
from .content import CONCEPTS, CH_WEIGHT, MCQ_GENERATORS, SQL_GENERATORS
# SQL courses also export SAMPLE_DBS / DB_DESCRIPTIONS from content.py:
# from .content import SAMPLE_DBS, DB_DESCRIPTIONS

# REQUIRED STIPULATION — every pack declares its playground explicitly:
#   PLAYGROUND = SqlPlayground(SAMPLE_DBS, DB_DESCRIPTIONS)  # database courses
#   PLAYGROUND = PythonPlayground()                          # from core.playgrounds.python_runner
#   PLAYGROUND = YourInterpreter()   # single-course backend lives IN the pack
#   PLAYGROUND = None                # + PLAYGROUND_NOTE explaining why
# The harness fails packs that stay silent. See skills/course-pack-creator.
PLAYGROUND = None
PLAYGROUND_NOTE = "Template demo — concept drills only."
