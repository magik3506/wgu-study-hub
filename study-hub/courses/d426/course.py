"""D426 pack manifest — the contract every course folder provides."""
COURSE = {
    "code": "D426",
    "slug": "d426",
    "name": "Data Management \u2014 Foundations",
    "blurb": ("MySQL playground on the course's own lab tables, exam drills "
              "weighted like the real OA, and hands-on SQL graded live."),
    "status": "active",          # active | template (hidden)
    "badge": "OA BLUEPRINT \u00b7 SQL 38 \u00b7 ER 24 \u00b7 NF 21",
    "chapter_names": {1: "Introduction", 2: "Data definition", 3: "Queries",
                      4: "ER modeling & normal forms", 5: "Physical design"},
    "topics": [("joins", "Joins"), ("normal", "Normal forms"),
               ("cardinal", "Cardinality & modality"),
               ("keys", "Primary & foreign keys"),
               ("constraint", "Constraints & ref. integrity"),
               ("types", "Data types"), ("null", "NULL handling"),
               ("alter", "ALTER TABLE"), ("view", "Views"),
               ("index", "Indexes & storage")],
}
from .content import (CONCEPTS, CH_WEIGHT, SAMPLE_DBS, DB_DESCRIPTIONS,
                      MCQ_GENERATORS, SQL_GENERATORS)

from core.playgrounds.sql import SqlPlayground
PLAYGROUND = SqlPlayground(
    SAMPLE_DBS, DB_DESCRIPTIONS,
    placeholder=("-- MySQL, the way D426 teaches it\n"
                 "SHOW TABLES;\n"
                 "SELECT RegisteredName, Breed, Height FROM Horse "
                 "WHERE Height > 15;"))
