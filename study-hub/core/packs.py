"""Course-pack discovery. A pack = courses/<slug>/course.py exposing COURSE
plus CONCEPTS, CH_WEIGHT, MCQ_GENERATORS, SQL_GENERATORS, and (for SQL
courses) SAMPLE_DBS / DB_DESCRIPTIONS. Drop a folder in, restart, it's live."""
import importlib
import os

COURSES_ROOT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "courses")

class Pack:
    def __init__(self, slug, mod):
        m = mod.COURSE
        self.slug = m.get("slug", slug)
        self.code = m["code"]
        self.name = m["name"]
        self.blurb = m.get("blurb", "")
        self.status = m.get("status", "active")
        self.badge = m.get("badge", "ADAPTIVE DRILLS")
        self.chapter_names = m.get("chapter_names", {})
        self.unit_label = m.get("unit_label", "Chapter")
        self.topics = m.get("topics", [])
        self.concepts = mod.CONCEPTS
        self.ch_weight = mod.CH_WEIGHT
        self.mcq_generators = getattr(mod, "MCQ_GENERATORS", [])
        self.sql_generators = getattr(mod, "SQL_GENERATORS", [])
        self.sample_dbs = getattr(mod, "SAMPLE_DBS", {}) or {}
        self.playground = getattr(mod, "PLAYGROUND", "__unstipulated__")
        self.playground_note = getattr(mod, "PLAYGROUND_NOTE", "")
        self.db_descriptions = getattr(mod, "DB_DESCRIPTIONS", {}) or {}
        self.dir = os.path.join(COURSES_ROOT, slug)

    @property
    def has_playground(self):
        return (self.playground is not None
                and self.playground != "__unstipulated__")

    @property
    def study_guide_path(self):
        p = os.path.join(self.dir, "study_guide.pdf")
        return p if os.path.exists(p) else None

def discover(include_template=False):
    packs = []
    if not os.path.isdir(COURSES_ROOT):
        return packs
    for slug in sorted(os.listdir(COURSES_ROOT)):
        d = os.path.join(COURSES_ROOT, slug)
        if not os.path.isdir(d) or not os.path.exists(
                os.path.join(d, "course.py")):
            continue
        mod = importlib.import_module(f"courses.{slug}.course")
        p = Pack(slug, mod)
        if p.status == "template" and not include_template:
            continue
        packs.append(p)
    return packs

def data_dir_for(slug):
    root = os.environ.get("WGU_HUB_HOME") or os.path.join(
        os.path.expanduser("~"), ".wgu_study_hub")
    return os.path.join(root, slug)
