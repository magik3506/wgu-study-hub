"""MySQL-flavored SQL engine on SQLite: translation layer + Engine.
Course-agnostic: sample databases and data dir are constructor params."""
import datetime as _dt
import os
import re
import shutil
import sqlite3
import time

from .ui import red, dim, print_result

# ---------------------------------------------------------------------------
# MySQL compatibility layer
# ---------------------------------------------------------------------------
# The goal is not a perfect MySQL clone; it is "the MySQL that D426 teaches":
# CREATE/ALTER/DROP, constraints, AUTO_INCREMENT, SHOW/DESCRIBE, the string
# and date functions from chapter 3, joins (including FULL JOIN with a note
# that real MySQL lacks it), views, and indexes.

_ident = r"[A-Za-z_][A-Za-z0-9_]*"

def _strip_mysql_noise(sql):
    """Remove MySQL-only decorations SQLite can't parse."""
    notes = []
    s = sql
    s = s.replace("`", "")
    # table options
    s2 = re.sub(r"\bENGINE\s*=\s*\w+", "", s, flags=re.I)
    s2 = re.sub(r"\bDEFAULT\s+CHARSET\s*=\s*\w+", "", s2, flags=re.I)
    s2 = re.sub(r"\bAUTO_INCREMENT\s*=\s*\d+", "", s2, flags=re.I)
    if s2 != s:
        s = s2
    # UNSIGNED / ZEROFILL
    if re.search(r"\bUNSIGNED\b", s, flags=re.I):
        notes.append("UNSIGNED accepted but not enforced by this engine "
                     "(in MySQL it doubles the positive range).")
        s = re.sub(r"\bUNSIGNED\b", "", s, flags=re.I)
    s = re.sub(r"\bZEROFILL\b", "", s, flags=re.I)
    # ENUM(...) -> TEXT
    if re.search(r"\bENUM\s*\(", s, flags=re.I):
        notes.append("ENUM stored as TEXT here (values not restricted); "
                     "the course restricts values with CHECK constraints instead.")
        s = re.sub(r"\bENUM\s*\([^)]*\)", "TEXT", s, flags=re.I)
    return s, notes

def _fix_auto_increment(sql):
    """Map `col INT ... AUTO_INCREMENT` onto SQLite's INTEGER PRIMARY KEY rowid
    behavior, which auto-increments exactly the way the course expects."""
    notes = []
    if not re.search(r"\bAUTO_INCREMENT\b", sql, flags=re.I):
        return sql, notes
    s = re.sub(
        r"\b(TINYINT|SMALLINT|MEDIUMINT|BIGINT|INTEGER|INT)\b"      # type
        r"((?:\s*\([^)]*\))?)"                                       # (n)
        r"([^,()]*?)\bAUTO_INCREMENT\b",
        lambda m: "INTEGER" + m.group(3),
        sql, flags=re.I)
    if re.search(r"\bAUTO_INCREMENT\b", s, flags=re.I):
        # AUTO_INCREMENT appeared somewhere unusual; drop it rather than fail.
        s = re.sub(r"\bAUTO_INCREMENT\b", "", s, flags=re.I)
    return s, notes

def _translate_alter(sql):
    """Handle MySQL ALTER TABLE forms the course teaches (the CAD verbs:
    CHANGE, ADD, DROP) plus ADD FOREIGN KEY."""
    notes = []
    m = re.match(r"\s*ALTER\s+TABLE\s+(" + _ident + r")\s+(.*)$",
                 sql, flags=re.I | re.S)
    if not m:
        return [sql], notes
    table, rest = m.group(1), m.group(2).strip().rstrip(";").strip()

    # CHANGE oldName newName TYPE  -> rename (SQLite cannot retype a column)
    cm = re.match(r"CHANGE\s+(COLUMN\s+)?(" + _ident + r")\s+(" + _ident + r")\s+(.+)$",
                  rest, flags=re.I | re.S)
    if cm:
        old, new, newtype = cm.group(2), cm.group(3), cm.group(4).strip()
        stmts = []
        if old.lower() != new.lower():
            stmts.append(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new}")
            notes.append(f"CHANGE: renamed {old} -> {new}. The new type "
                         f"({newtype}) is noted but this engine keeps the stored "
                         f"type; real MySQL would also convert the column type.")
        else:
            notes.append(f"CHANGE: in MySQL this would set {old} to {newtype}. "
                         "This engine cannot retype an existing column, so the "
                         "statement is a no-op here — but your syntax is what "
                         "the exam grades, and it is correct.")
            stmts.append("SELECT 1 WHERE 0")  # harmless no-op
        return stmts, notes

    mm = re.match(r"MODIFY\s+(COLUMN\s+)?(" + _ident + r")\s+(.+)$", rest, flags=re.I | re.S)
    if mm:
        notes.append("MODIFY changes a column's type in MySQL; this engine "
                     "cannot retype columns, so it's a no-op here. "
                     "(Exam tip: MySQL's course-taught verbs are CHANGE, ADD, DROP.)")
        return ["SELECT 1 WHERE 0"], notes

    # ADD FOREIGN KEY (col) REFERENCES T(col)
    fm = re.match(r"ADD\s+(CONSTRAINT\s+" + _ident + r"\s+)?FOREIGN\s+KEY\s*\(([^)]+)\)\s*"
                  r"REFERENCES\s+(" + _ident + r")\s*\(([^)]+)\)\s*(.*)$",
                  rest, flags=re.I | re.S)
    if fm:
        notes.append("Correct MySQL syntax. SQLite can't add a FOREIGN KEY to an "
                     "existing table, so the constraint isn't enforced here — in "
                     "real MySQL, ALTER TABLE ... ADD FOREIGN KEY (col) "
                     "REFERENCES Parent(col) attaches it immediately.")
        return ["SELECT 1 WHERE 0"], notes

    um = re.match(r"ADD\s+(CONSTRAINT\s+" + _ident + r"\s+)?UNIQUE\s*\(([^)]+)\)\s*$",
                  rest, flags=re.I)
    if um:
        cols = um.group(2)
        idx = "Uniq_" + table + "_" + re.sub(r"\W+", "_", cols)
        return [f"CREATE UNIQUE INDEX {idx} ON {table} ({cols})"], notes

    # ADD [COLUMN] def   /  DROP [COLUMN] name  — MySQL allows omitting COLUMN
    am = re.match(r"ADD\s+(?!COLUMN\b)(" + _ident + r"\s+.+)$", rest, flags=re.I | re.S)
    if am:
        return [f"ALTER TABLE {table} ADD COLUMN {am.group(1)}"], notes
    dm = re.match(r"DROP\s+(?!COLUMN\b)(" + _ident + r")\s*$", rest, flags=re.I)
    if dm:
        return [f"ALTER TABLE {table} DROP COLUMN {dm.group(1)}"], notes

    return [sql.rstrip().rstrip(";")], notes

def translate_sql(sql):
    """MySQL-dialect statement -> list of SQLite statements + info notes.
    Meta statements (SHOW, DESCRIBE, USE, ...) are handled before this."""
    notes = []
    s = sql
    # strip `#` comments (MySQL-only) at line starts
    lines = []
    for line in s.split("\n"):
        if line.lstrip().startswith("#"):
            continue
        lines.append(line)
    s = "\n".join(lines)

    s, n = _strip_mysql_noise(s);      notes += n
    s, n = _fix_auto_increment(s);     notes += n

    if re.match(r"\s*INSERT\s+IGNORE\b", s, flags=re.I):
        s = re.sub(r"^\s*INSERT\s+IGNORE\b", "INSERT OR IGNORE", s, flags=re.I)

    tm = re.match(r"\s*TRUNCATE\s+(TABLE\s+)?(" + _ident + r")\s*;?\s*$", s, flags=re.I)
    if tm:
        t = tm.group(2)
        notes.append("TRUNCATE deletes all rows but keeps the table structure "
                     "(unlike DROP TABLE, which deletes the table itself).")
        return ([f"DELETE FROM {t}"], notes)

    if re.match(r"\s*ALTER\s+TABLE\b", s, flags=re.I):
        stmts, n = _translate_alter(s)
        return stmts, notes + n

    if re.search(r"\bFULL\s+(OUTER\s+)?JOIN\b", s, flags=re.I):
        notes.append("Heads up for the exam: real MySQL does NOT support FULL "
                     "JOIN. You emulate it with a LEFT JOIN, UNION, RIGHT JOIN. "
                     "This sandbox runs it anyway so you can study the concept.")

    if re.match(r"\s*DROP\s+INDEX\s+(" + _ident + r")\s*;?\s*$", s, flags=re.I):
        # MySQL: DROP INDEX name ON table;  bare form also seen in course slides.
        pass  # SQLite's bare DROP INDEX name works directly.
    dm = re.match(r"\s*DROP\s+INDEX\s+(" + _ident + r")\s+ON\s+" + _ident + r"\s*;?\s*$",
                  s, flags=re.I)
    if dm:
        s = f"DROP INDEX {dm.group(1)}"

    return [s.rstrip().rstrip(";")], notes

# --- MySQL functions missing from SQLite -----------------------------------

def _to_date(v):
    if v is None:
        return None
    s = str(v)
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None

def _to_time(v):
    if v is None:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", str(v))
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)) if m else None

def _fn_concat(*args):
    if any(a is None for a in args):
        return None
    return "".join(str(a) for a in args)

def _fn_concat_ws(sep, *args):
    if sep is None:
        return None
    return str(sep).join(str(a) for a in args if a is not None)

def _fn_datediff(a, b):
    da, db_ = _to_date(a), _to_date(b)
    if not da or not db_:
        return None
    return (_dt.date(*da) - _dt.date(*db_)).days

def register_mysql_functions(conn):
    """Add the chapter-3 MySQL functions SQLite lacks."""
    def have(expr):
        try:
            conn.execute("SELECT " + expr)
            return True
        except sqlite3.OperationalError:
            return False

    def reg(name, n, fn):
        try:
            conn.create_function(name, n, fn)
        except sqlite3.OperationalError:
            pass

    if not have("CONCAT('a','b')"):
        reg("CONCAT", -1, _fn_concat)
    reg("CONCAT_WS", -1, _fn_concat_ws)
    reg("YEAR", 1, lambda v: (_to_date(v) or (None,))[0])
    reg("MONTH", 1, lambda v: (lambda d: d[1] if d else None)(_to_date(v)))
    reg("DAY", 1, lambda v: (lambda d: d[2] if d else None)(_to_date(v)))
    reg("DAYOFMONTH", 1, lambda v: (lambda d: d[2] if d else None)(_to_date(v)))
    reg("HOUR", 1, lambda v: (lambda t: t[0] if t else None)(_to_time(v)))
    reg("MINUTE", 1, lambda v: (lambda t: t[1] if t else None)(_to_time(v)))
    reg("SECOND", 1, lambda v: (lambda t: t[2] if t else None)(_to_time(v)))
    reg("NOW", 0, lambda: _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    reg("CURDATE", 0, lambda: _dt.date.today().isoformat())
    reg("CURTIME", 0, lambda: _dt.datetime.now().strftime("%H:%M:%S"))
    reg("DATEDIFF", 2, _fn_datediff)
    reg("LEFT", 2, lambda s, n: None if s is None or n is None else str(s)[:max(int(n), 0)])
    reg("RIGHT", 2, lambda s, n: None if s is None or n is None
        else (str(s)[-int(n):] if int(n) > 0 else ""))
    reg("LCASE", 1, lambda s: None if s is None else str(s).lower())
    reg("UCASE", 1, lambda s: None if s is None else str(s).upper())
    reg("REPEAT", 2, lambda s, n: None if s is None or n is None else str(s) * int(n))
    reg("REVERSE", 1, lambda s: None if s is None else str(s)[::-1])
    reg("LOCATE", 2, lambda sub, s: None if sub is None or s is None
        else str(s).find(str(sub)) + 1)
    reg("CHAR_LENGTH", 1, lambda s: None if s is None else len(str(s)))
    reg("IF", 3, lambda c, a, b: a if c not in (None, 0, "0", False) else b)
    if not have("MOD(5,2)"):
        reg("MOD", 2, lambda a, b: None if a is None or b is None else a % b)
    if not have("POW(2,3)"):
        reg("POW", 2, lambda a, b: None if a is None or b is None else a ** b)
    if not have("POWER(2,3)"):
        reg("POWER", 2, lambda a, b: None if a is None or b is None else a ** b)
    if not have("FLOOR(1.5)"):
        import math
        reg("FLOOR", 1, lambda v: None if v is None else math.floor(v))
        reg("CEIL", 1, lambda v: None if v is None else math.ceil(v))
        reg("CEILING", 1, lambda v: None if v is None else math.ceil(v))
        reg("SQRT", 1, lambda v: None if v is None else math.sqrt(v))
    if not have("SUBSTRING('abc',1,2)"):
        reg("SUBSTRING", 3, lambda s, p, l: None if s is None
            else str(s)[int(p) - 1:int(p) - 1 + int(l)])
        reg("SUBSTRING", 2, lambda s, p: None if s is None else str(s)[int(p) - 1:])
    reg("RAND", 0, lambda: random.random())


# ---------------------------------------------------------------------------
# Engine: one SQLite file per sample database, MySQL dialect in front
# ---------------------------------------------------------------------------

class Engine:
    def __init__(self, data_dir, sample_dbs, descriptions=None, default_db=None):
        self.data_dir = data_dir
        self.db_dir = os.path.join(data_dir, "dbs")
        self.sample_dbs = dict(sample_dbs)
        self.descriptions = descriptions or {}
        os.makedirs(self.db_dir, exist_ok=True)
        self.current = default_db or (next(iter(self.sample_dbs))
                                      if self.sample_dbs else None)
        self._conns = {}
        for name in self.sample_dbs:
            if not os.path.exists(self._path(name)):
                self._build(name)

    def _path(self, name):
        return os.path.join(self.db_dir, name + ".db")

    def _connect(self, name):
        if name in self._conns:
            return self._conns[name]
        conn = sqlite3.connect(self._path(name), check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        register_mysql_functions(conn)
        self._conns[name] = conn
        return conn

    def _build(self, name):
        path = self._path(name)
        if os.path.exists(path):
            os.remove(path)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        register_mysql_functions(conn)
        for stmt in split_statements(self.sample_dbs[name]):
            for s2, _n in [translate_sql(stmt)]:
                for s3 in s2:
                    conn.execute(s3)
        conn.commit()
        conn.close()
        self._conns.pop(name, None)

    @property
    def conn(self):
        return self._connect(self.current)

    def databases(self):
        names = set(self.sample_dbs)
        for f in os.listdir(self.db_dir):
            if f.endswith(".db"):
                names.add(f[:-3])
        return sorted(names)

    def use(self, name):
        if name not in self.databases():
            raise ValueError(f"Unknown database '{name}'. Try SHOW DATABASES;")
        self.current = name

    def create_database(self, name):
        if not re.match(r"^" + _ident + r"$", name):
            raise ValueError("Invalid database name.")
        if name in self.databases():
            raise ValueError(f"Database '{name}' already exists.")
        sqlite3.connect(self._path(name)).close()

    def drop_database(self, name):
        if name in self.sample_dbs:
            raise ValueError(f"'{name}' is a sample database — use `reset {name}` "
                             "to restore it instead.")
        p = self._path(name)
        if not os.path.exists(p):
            raise ValueError(f"Unknown database '{name}'.")
        self._conns.pop(name, None)
        os.remove(p)
        if self.current == name:
            self.current = "stable"

    def reset(self, name=None):
        targets = [name] if name else list(self.sample_dbs)
        for t in targets:
            if t not in self.sample_dbs:
                raise ValueError(f"'{t}' is not a sample database.")
            self._conns.pop(t, None)
            self._build(t)

    def tables(self, name=None):
        conn = self._connect(name or self.current)
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        return [r[0] for r in rows]

    def describe(self, table):
        conn = self.conn
        info = conn.execute(f"PRAGMA table_info({table})").fetchall()
        if not info:
            raise ValueError(f"Table '{table}' doesn't exist in {self.current}.")
        uniq_cols = set()
        for idx in conn.execute(f"PRAGMA index_list({table})").fetchall():
            # idx: (seq, name, unique, origin, partial)
            if idx[2]:
                cols = conn.execute(f"PRAGMA index_info({idx[1]})").fetchall()
                if len(cols) == 1:
                    uniq_cols.add(cols[0][2])
        rows = []
        for cid, name, ctype, notnull, dflt, pk in info:
            key = "PRI" if pk else ("UNI" if name in uniq_cols else "")
            extra = "auto_increment" if (pk == 1 and (ctype or "").upper() == "INTEGER"
                                         and sum(1 for i in info if i[5]) == 1) else ""
            rows.append((name, ctype or "", "NO" if notnull or pk else "YES",
                         key, dflt if dflt is not None else "NULL", extra))
        return ["Field", "Type", "Null", "Key", "Default", "Extra"], rows

    def run(self, sql):
        """Execute one MySQL-dialect statement and return a structured result:
        {ok, headers, rows, message, notes, elapsed, db}. This is the
        UI-agnostic core; execute() renders it for the terminal."""
        res = {"ok": True, "headers": None, "rows": None, "message": None,
               "notes": [], "elapsed": None, "db": self.current}
        if self._meta(sql, res):
            res["db"] = self.current
            return res
        stmts, notes = translate_sql(sql)
        res["notes"] = notes
        conn = self.conn
        t0 = time.time()
        try:
            cur = None
            for s in stmts:
                if not s.strip():
                    continue
                cur = conn.execute(s)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            res["ok"] = False
            res["message"] = mysqlify_error(str(e), sql)
            res["db"] = self.current
            return res
        res["elapsed"] = time.time() - t0
        if cur is not None and cur.description:
            res["headers"] = [d[0] for d in cur.description]
            res["rows"] = cur.fetchall()
        else:
            affected = cur.rowcount if cur is not None and cur.rowcount >= 0 else 0
            res["message"] = (f"Query OK, {affected} "
                              f"row{'s' if affected != 1 else ''} affected")
        res["db"] = self.current
        return res

    def execute(self, sql, out=None):
        """Run one MySQL-dialect statement; print results. Returns True if OK."""
        p = (out.append if out is not None else print)
        res = self.run(sql)
        if not res["ok"]:
            p(red("ERROR: ") + str(res["message"]))
            for n in res["notes"]:
                p(dim("  i " + n))
            return False
        if res["headers"] is not None:
            print_result(res["headers"], res["rows"], res["elapsed"], out=out)
        elif res["message"]:
            el = (f" ({res['elapsed']:.3f} sec)"
                  if res["elapsed"] is not None else "")
            p(dim(res["message"] + el))
        for n in res["notes"]:
            p(dim("  i " + n))
        return True

    def query(self, sql, db=None):
        """Run a SELECT quietly; return (headers, rows). Raises on error."""
        conn = self._connect(db or self.current)
        stmts, _ = translate_sql(sql)
        cur = None
        for s in stmts:
            if s.strip():
                cur = conn.execute(s)
        if cur is None or not cur.description:
            return [], []
        return [d[0] for d in cur.description], cur.fetchall()

    def _meta(self, sql, res):
        """Handle MySQL meta statements, filling `res`. True if handled."""
        s = sql.strip().rstrip(";").strip()
        low = s.lower()
        if low == "show databases":
            res["headers"] = ["Database"]
            res["rows"] = [(d,) for d in self.databases()]
            return True
        if low == "show tables":
            res["headers"] = [f"Tables_in_{self.current}"]
            res["rows"] = [(t,) for t in self.tables()]
            return True
        m = re.match(r"show\s+columns\s+from\s+(" + _ident + r")$", low)
        if m or low.startswith("describe ") or low.startswith("desc "):
            table = m.group(1) if m else s.split()[1]
            try:
                res["headers"], res["rows"] = self.describe(table)
            except ValueError as e:
                res["ok"] = False
                res["message"] = str(e)
            return True
        m = re.match(r"show\s+create\s+table\s+(" + _ident + r")$", low)
        if m:
            row = self.conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' "
                "AND lower(name)=lower(?)", (m.group(1),)).fetchone()
            if not row:
                res["ok"] = False
                res["message"] = f"Table '{m.group(1)}' doesn't exist."
                return True
            res["headers"] = ["Table", "Create Table"]
            res["rows"] = [(m.group(1), row[0])]
            res["notes"].append("Shown as stored by this engine (translated "
                                "from MySQL syntax).")
            return True
        m = re.match(r"show\s+(index|indexes|keys)\s+from\s+(" + _ident + r")$", low)
        if m:
            t = m.group(2)
            rows = self.conn.execute(f"PRAGMA index_list({t})").fetchall()
            res["headers"] = ["Table", "Key_name", "Non_unique"]
            res["rows"] = [(t, r[1], "no" if r[2] else "yes") for r in rows]
            return True
        m = re.match(r"use\s+(" + _ident + r")$", low)
        if m:
            try:
                self.use(m.group(1))
                res["message"] = f"Database changed to {self.current}"
            except ValueError as e:
                res["ok"] = False
                res["message"] = str(e)
            return True
        m = re.match(r"create\s+database\s+(if\s+not\s+exists\s+)?(" + _ident + r")$", low)
        if m:
            try:
                self.create_database(m.group(2))
                res["message"] = f"Query OK, database '{m.group(2)}' created"
            except ValueError as e:
                res["ok"] = False
                res["message"] = str(e)
            return True
        m = re.match(r"drop\s+database\s+(" + _ident + r")$", low)
        if m:
            try:
                self.drop_database(m.group(1))
                res["message"] = "Query OK, database dropped"
            except ValueError as e:
                res["ok"] = False
                res["message"] = str(e)
            return True
        return False

def mysqlify_error(msg, sql=""):
    """Reword common SQLite errors into the MySQL vocabulary D426 uses."""
    m = msg
    if "FOREIGN KEY constraint failed" in m:
        if re.match(r"\s*(DELETE|UPDATE)", sql or "", flags=re.I):
            return ("Cannot delete or update a parent row: a foreign key "
                    "constraint fails (rows in a child table still reference "
                    "it — that is referential integrity with the default "
                    "RESTRICT action).")
        return ("Cannot add or update a child row: a foreign key constraint "
                "fails (referential integrity — the foreign key value must "
                "exist in the parent table).")
    if "UNIQUE constraint failed" in m and ".": 
        col = m.split("failed:")[-1].strip()
        return f"Duplicate entry for key '{col}' (UNIQUE/PRIMARY KEY constraint)."
    if "NOT NULL constraint failed" in m:
        col = m.split("failed:")[-1].strip()
        return f"Column '{col}' cannot be null (NOT NULL constraint)."
    if "CHECK constraint failed" in m:
        return "Check constraint violated: " + m.split("failed:")[-1].strip()
    if "no such table" in m:
        return m.replace("no such table:", "Table doesn't exist:")
    if "no such column" in m:
        return m.replace("no such column:", "Unknown column:")
    if "syntax error" in m:
        return m + dim("  (check keyword order and commas)")
    return m

def split_statements(script):
    """Split a script on ';' while respecting single-quoted strings."""
    stmts, buf, in_str = [], [], False
    i = 0
    while i < len(script):
        ch = script[i]
        if ch == "'":
            if in_str and i + 1 < len(script) and script[i + 1] == "'":
                buf.append("''"); i += 2; continue
            in_str = not in_str
            buf.append(ch)
        elif ch == ";" and not in_str:
            stmt = "".join(buf).strip()
            stmt = re.sub(r"^\s*--[^\n]*\n?", "", stmt, flags=re.M).strip()
            if stmt:
                stmts.append(stmt)
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    tail = re.sub(r"^\s*--[^\n]*\n?", "", tail, flags=re.M).strip()
    if tail:
        stmts.append(tail)
    return stmts

