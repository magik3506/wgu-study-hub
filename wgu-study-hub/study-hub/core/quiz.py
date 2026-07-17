"""Course-agnostic quiz machinery: fresh-copy execution context,
execution-based grading, adaptive selection, stats."""
import json
import os
import random
import re
import sqlite3

from .engine import (translate_sql, split_statements,
                     register_mysql_functions, mysqlify_error)

class QuizContext:
    """Runs quiz SQL on FRESH in-memory copies of the sample databases, so
    grading is deterministic no matter what you've done in the playground."""

    def __init__(self, sample_dbs):
        self._dbs = dict(sample_dbs)

    def _fresh(self, db):
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON")
        register_mysql_functions(conn)
        if db:
            for stmt in split_statements(self._dbs[db]):
                for s in translate_sql(stmt)[0]:
                    conn.execute(s)
            conn.commit()
        return conn

    def q(self, db, sql, setup=None):
        conn = self._fresh(db)
        try:
            if setup:
                for s in setup:
                    for s2 in translate_sql(s)[0]:
                        conn.execute(s2)
            cur = None
            for stmt in split_statements(sql):
                for s2 in translate_sql(stmt)[0]:
                    if s2.strip():
                        cur = conn.execute(s2)
            if cur is not None and cur.description:
                return [d[0] for d in cur.description], cur.fetchall()
            return [], []
        finally:
            conn.close()

def _norm_rows(rows, ordered):
    def nv(v):
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return round(float(v), 4)
        return v
    out = [tuple(nv(v) for v in r) for r in rows]
    if not ordered:
        out.sort(key=lambda r: tuple((str(type(x)), str(x)) for x in r))
    return out

def _apply_user_sql(conn, user_sql):
    for stmt in split_statements(user_sql):
        for s2 in translate_sql(stmt)[0]:
            if s2.strip():
                conn.execute(s2)

def check_sql_task(task, user_sql, ctx):
    """Grade a hands-on SQL answer. Returns (ok, feedback_lines)."""
    fb = []
    db = task["db"]
    kind = task["kind"]
    try:
        if kind == "select":
            uh, ur = ctx.q(db, user_sql)
            rh, rr = ctx.q(db, task["reference"])
            if len(uh) != len(rh):
                fb.append(f"Expected {len(rh)} column(s) "
                          f"({', '.join(rh)}) but got {len(uh)}.")
                return False, fb
            ok = _norm_rows(ur, task["order_matters"]) == \
                 _norm_rows(rr, task["order_matters"])
            if not ok:
                fb.append(f"Expected {len(rr)} row(s), got {len(ur)}.")
                if task["order_matters"] and \
                   _norm_rows(ur, False) == _norm_rows(rr, False):
                    fb.append("Same rows, wrong ORDER — check your ORDER BY.")
            return ok, fb
        if kind == "dml":
            uconn = ctx._fresh(db)
            rconn = ctx._fresh(db)
            try:
                _apply_user_sql(uconn, user_sql)
                _apply_user_sql(rconn, task["reference"])
                vh = task["verify"]
                ucur = None
                for s2 in translate_sql(vh)[0]:
                    ucur = uconn.execute(s2)
                ur = ucur.fetchall()
                rcur = None
                for s2 in translate_sql(vh)[0]:
                    rcur = rconn.execute(s2)
                rr = rcur.fetchall()
                ok = _norm_rows(ur, False) == _norm_rows(rr, False)
                if not ok:
                    fb.append("After your statement ran, the table doesn't "
                              "match the expected state.")
                return ok, fb
            finally:
                uconn.close(); rconn.close()
        if kind == "ddl":
            conn = ctx._fresh(db)
            try:
                _apply_user_sql(conn, user_sql)
                spec = task["ddl_check"]
                t = spec["table"]
                info = conn.execute(f"PRAGMA table_info({t})").fetchall()
                if not info:
                    fb.append(f"Table {t} was not created.")
                    return False, fb
                cols = {r[1].lower(): (r[2] or "").upper() for r in info}
                pkcols = {r[1].lower() for r in info if r[5]}
                for cname, ctype in spec.get("has_columns", []):
                    if cname.lower() not in cols:
                        fb.append(f"Missing column {cname}.")
                        return False, fb
                    actual = cols[cname.lower()]
                    want = ctype.upper()
                    type_ok = (want in actual or
                               (want == "INT" and "INT" in actual) or
                               (want == "DECIMAL" and ("DEC" in actual or "NUM" in actual)))
                    if not type_ok:
                        fb.append(f"Column {cname}: expected a {ctype}-style "
                                  f"type, found {actual or '(none)'}.")
                        return False, fb
                if "pk" in spec:
                    want_pk = {c.lower() for c in spec["pk"]}
                    if pkcols != want_pk:
                        fb.append(f"Primary key should be "
                                  f"({', '.join(spec['pk'])}); found "
                                  f"({', '.join(sorted(pkcols)) or 'none'}).")
                        return False, fb
                if "fks" in spec:
                    fklist = conn.execute(f"PRAGMA foreign_key_list({t})").fetchall()
                    have = {(r[3].lower(), r[2].lower()) for r in fklist}
                    for col, parent in spec["fks"]:
                        if (col.lower(), parent.lower()) not in have:
                            fb.append(f"Missing FOREIGN KEY from {col} to "
                                      f"{parent}.")
                            return False, fb
                return True, fb
            finally:
                conn.close()
    except sqlite3.Error as e:
        fb.append("Your SQL raised an error: " + mysqlify_error(str(e)))
        return False, fb
    return False, ["Unknown task kind."]

# --- Stats -------------------------------------------------------------------

def load_stats(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}

def save_stats(st, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(st, f, indent=1)

def record_result(st, cid, ok):
    d = st.setdefault(cid, {"a": 0, "c": 0})
    d["a"] += 1
    d["c"] += 1 if ok else 0

def concept_weight(st, cid, concepts, ch_weight):
    ch = concepts[cid]["ch"]
    base = ch_weight[ch]
    d = st.get(cid)
    if not d or d["a"] == 0:
        return base * 1.3            # unseen concepts get a look-in
    wrong = 1.0 - d["c"] / d["a"]
    if d["a"] >= 3 and wrong == 0:
        return base * 0.55           # mastered: still appears, less often
    return base * (1.0 + 2.5 * wrong)

def pick_questions(n, st, rng, ctx, source, concepts, ch_weight, topic=None):
    gens = list(source)
    cands, tries = [], 0
    while len(cands) < n * 6 and tries < n * 40:
        tries += 1
        gen = rng.choice(gens)
        try:
            q = gen(rng, ctx)
        except Exception:
            continue
        if topic is not None and not _topic_match(q, topic, concepts):
            continue
        cands.append(q)
    chosen, seen_prompts, per_concept = [], set(), {}
    while cands and len(chosen) < n:
        weights = [concept_weight(st, c["concept"], concepts, ch_weight) for c in cands]
        total = sum(weights)
        r = rng.random() * total
        acc, idx = 0.0, 0
        for i, w in enumerate(weights):
            acc += w
            if acc >= r:
                idx = i
                break
        q = cands.pop(idx)
        key = q["prompt"][:80]
        if key in seen_prompts:
            continue
        if per_concept.get(q["concept"], 0) >= 2 and len(cands) > (n - len(chosen)):
            continue
        seen_prompts.add(key)
        per_concept[q["concept"]] = per_concept.get(q["concept"], 0) + 1
        chosen.append(q)
    return chosen

def _topic_match(q, topic, concepts):
    t = topic.strip().lower()
    c = concepts[q["concept"]]
    if t.startswith("ch") and t[2:].isdigit():
        return c["ch"] == int(t[2:])
    if t.isdigit():
        return c["ch"] == int(t)
    hay = (q["concept"] + " " + c["name"] + " " + c["ref"]).lower()
    return t in hay

# --- Quiz session ------------------------------------------------------------


def _scratch_tables(ctx, db):
    conn = ctx._fresh(db)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' "
                            "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()

