"""SQL playground backend — wraps the MySQL-on-SQLite Engine.
The reference implementation of the playground port; used by D426/D427."""
from ..engine import Engine, split_statements
from . import PlaygroundBase, rows_json

class SqlPlayground(PlaygroundBase):
    kind = "sql"
    label = "SQL console"
    stdin_enabled = False

    def __init__(self, sample_dbs, descriptions=None, placeholder=None):
        self._dbs = dict(sample_dbs)
        self._desc = descriptions or {}
        self.placeholder = placeholder or ("-- MySQL syntax\nSHOW TABLES;")
        self.engine = None

    def bind(self, data_dir):
        self.data_dir = data_dir
        self.engine = Engine(data_dir, self._dbs, self._desc)

    def run(self, source, stdin=""):
        blocks, top_notes, ok = [], [], True
        for stmt in split_statements(str(source))[:20]:
            r = self.engine.run(stmt)
            notes = list(r.get("notes") or [])
            if not r["ok"]:
                blocks.append({"kind": "error",
                               "text": "ERROR: " + str(r["message"]),
                               "notes": notes})
                ok = False
                break
            if r["headers"] is not None:
                rj, total, trunc = rows_json(r["rows"])
                blocks.append({"kind": "table", "headers": list(r["headers"]),
                               "rows": rj, "total": total,
                               "truncated": trunc, "notes": notes})
            else:
                el = (" (%.3f sec)" % r["elapsed"]) if r.get("elapsed") \
                     is not None else ""
                blocks.append({"kind": "ok",
                               "text": str(r["message"]) + el,
                               "notes": notes})
        return {"ok": ok, "blocks": blocks, "notes": top_notes,
                "state": {"selector_current": self.engine.current}}

    def sidebar(self):
        eng = self.engine
        groups = []
        for name in eng.databases():
            items = []
            for t in eng.tables(name):
                pre = f"USE {name};\n"
                items.append({"label": t,
                              "title": "Preview rows",
                              "run": pre + f"SELECT * FROM {t} LIMIT 25;",
                              "alt_run": pre + f"DESCRIBE {t};",
                              "alt_title": "Describe columns"})
            groups.append({"name": name,
                           "desc": self._desc.get(name, ""),
                           "on": name == eng.current,
                           "reset": name in self._dbs,
                           "items": items})
        return {"title": "Databases",
                "sub": ('Click a table to preview it, or '
                        '<span class="mono">i</span> for its schema.'),
                "reset_all": "Restore all sample data",
                "groups": groups}

    def selector(self):
        return {"label": "database",
                "options": self.engine.databases(),
                "current": self.engine.current,
                "run_template": "USE {value};"}

    def reset(self, target=None):
        t = None if target in (None, "", "all") else target
        self.engine.reset(t)
        return ("All sample databases restored." if t is None
                else f"Database '{t}' restored.")

    def selfcheck(self):
        first = next(iter(self._dbs))
        return [("SELECT 1+1;", "", "2"),
                ("SHOW DATABASES;", "", first),
                (f"USE {first};\nSHOW TABLES;", "", "Tables_in_" + first)]
