"""Terminal interface (REPL + drills) for any course pack.
Call init(pack, data_dir) once; module globals are injected from the pack
so the original REPL code runs unchanged."""
import argparse
import os
import random
import sys
import textwrap
import time

from . import quiz as _quiz
from .engine import Engine, mysqlify_error, split_statements, translate_sql
from .quiz import QuizContext, check_sql_task, pick_questions, record_result, _scratch_tables
from .ui import *

PACK = None
CONCEPTS = CH_WEIGHT = SAMPLE_DBS = DB_DESCRIPTIONS = None
MCQ_GENERATORS = SQL_GENERATORS = None
APP_DIR = STATS_PATH = HIST_PATH = None
VERSION = "2.0"

def init(pack, data_dir):
    global PACK, CONCEPTS, CH_WEIGHT, SAMPLE_DBS, DB_DESCRIPTIONS
    global MCQ_GENERATORS, SQL_GENERATORS, APP_DIR, STATS_PATH, HIST_PATH
    PACK = pack
    CONCEPTS, CH_WEIGHT = pack.concepts, pack.ch_weight
    SAMPLE_DBS, DB_DESCRIPTIONS = pack.sample_dbs, pack.db_descriptions
    MCQ_GENERATORS, SQL_GENERATORS = pack.mcq_generators, pack.sql_generators
    APP_DIR = data_dir
    STATS_PATH = os.path.join(APP_DIR, "stats.json")
    HIST_PATH = os.path.join(APP_DIR, "history")

def load_stats():
    return _quiz.load_stats(STATS_PATH)

def save_stats(st):
    _quiz.save_stats(st, STATS_PATH)

def _ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        return "q"

def _read_sql_answer():
    print(dim("  Type your SQL, end with ;   (or: hint / skip / q)"))
    buf = []
    while True:
        line = _ask(cyan("  sql> ") if not buf else cyan("   ...> "))
        w = line.strip().lower()
        if not buf and w in ("hint", "skip", "q", "quit", "exit"):
            return w
        buf.append(line)
        joined = "\n".join(buf)
        if _statement_complete(joined):
            return joined

def _statement_complete(text):
    in_str = False
    for i, ch in enumerate(text):
        if ch == "'":
            in_str = not in_str
    return (not in_str) and text.rstrip().endswith(";")

def _print_tag(q):
    c = CONCEPTS[q["concept"]]
    print(magenta(f"[Ch{c['ch']} §{c['ref']} · {c['name']}]"))


def run_quiz(st, n=10, mode="mcq", topic=None, rng=None):
    rng = rng or random.Random()
    ctx = QuizContext(SAMPLE_DBS)
    source = MCQ_GENERATORS if mode == "mcq" else SQL_GENERATORS
    label = ("Exam drill — multiple choice, weighted like the real OA"
             if mode == "mcq" else
             "Hands-on SQL drill — write real statements, graded live")
    qs = pick_questions(n, st, rng, ctx, source, CONCEPTS, CH_WEIGHT, topic)
    if not qs:
        print(yellow("No questions matched that topic. Try: drill joins, "
                     "drill normal, drill 4, drill er ..."))
        return
    print()
    print(bold(cyan(f"=== {label} ===")))
    if topic:
        print(dim(f"    focused on: {topic}"))
    print(dim(f"    {len(qs)} question{'s' if len(qs) != 1 else ''} · "
              + ("type SQL ending with ;" if mode == "sql"
                 else "answer with the letter")
              + ", or s=skip, q=quit\n"))
    results = []
    for i, q in enumerate(qs, 1):
        print(bold(f"Q{i}.") + " ", end="")
        _print_tag(q)
        print(wrap(q["prompt"], indent="  "))
        ok = None
        if q["type"] in ("mcq", "tf"):
            if q["type"] == "tf":
                opts = ["True", "False"]
                ans_idx = 0 if q["answer"] else 1
            else:
                opts = q["options"]
                ans_idx = q["answer"]
            letters = "ABCDE"[:len(opts)]
            for L, o in zip(letters, opts):
                print(f"    {bold(L)}. {wrap(str(o), width=72, indent='       ').lstrip()}")
            while ok is None:
                a = _ask(cyan("  your answer> ")).strip().lower()
                if a in ("q", "quit", "exit"):
                    print(dim("Quiz ended early."))
                    _quiz_summary(results, st)
                    return
                if a in ("s", "skip"):
                    ok = False
                    print(yellow("  — skipped. ") +
                          f"Answer: {bold(letters[ans_idx])}. {opts[ans_idx]}")
                    break
                if a in ("t", "true") and q["type"] == "tf":
                    a = "a"
                if a in ("f", "false") and q["type"] == "tf":
                    a = "b"
                if len(a) == 1 and a.upper() in letters:
                    picked = letters.index(a.upper())
                    ok = picked == ans_idx
                    if ok:
                        print(green("  ✔ Correct."))
                    else:
                        print(red("  ✘ Not quite. ") +
                              f"Answer: {bold(letters[ans_idx])}. {opts[ans_idx]}")
                else:
                    print(dim("  (enter a letter, s to skip, q to quit)"))
                    continue
            print(dim(wrap("» " + q["explain"], width=76, indent="  ")))
        else:  # sql task
            print(dim(f"  database: {q['db']} — tables: "
                      f"{', '.join(_scratch_tables(ctx, q['db']))}"))
            while True:
                ans = _read_sql_answer()
                if ans == "hint":
                    print(yellow("  hint: ") + (q.get("hint") or "—"))
                    continue
                if ans in ("q", "quit", "exit"):
                    print(dim("Quiz ended early."))
                    _quiz_summary(results, st)
                    return
                if ans == "skip":
                    ok = False
                    print(yellow("  — skipped."))
                    break
                ok, fb = check_sql_task(q, ans, ctx)
                if ok:
                    print(green("  ✔ Correct — your query produced the "
                                "expected result."))
                else:
                    print(red("  ✘ Not quite."))
                    for line in fb:
                        print(red("    " + line))
                break
            print(dim("  » Reference solution:"))
            print(dim("      " + q["reference"] + ";"))
            if q["kind"] == "select" and not ok:
                try:
                    rh, rr = ctx.q(q["db"], q["reference"])
                    outbuf = []
                    print_result(rh, rr, max_rows=6, out=outbuf)
                    print(dim("  Expected result:"))
                    for line in outbuf:
                        print(dim("    " + line))
                except Exception:
                    pass
        record_result(st, q["concept"], bool(ok))
        results.append((q, bool(ok)))
        print()
    _quiz_summary(results, st)


def _quiz_summary(results, st):
    save_stats(st)
    if not results:
        return
    n = len(results)
    right = sum(1 for _q, ok in results if ok)
    pct = 100.0 * right / n
    color = green if pct >= 80 else (yellow if pct >= 60 else red)
    print(bold("=== Session summary ==="))
    print("  Score: " + color(f"{right}/{n}  ({pct:.0f}%)"))
    by_ch = {}
    for q, ok in results:
        ch = CONCEPTS[q["concept"]]["ch"]
        a, c = by_ch.get(ch, (0, 0))
        by_ch[ch] = (a + 1, c + (1 if ok else 0))
    for ch in sorted(by_ch):
        a, c = by_ch[ch]
        bar = "█" * c + "░" * (a - c)
        print(f"    Ch{ch}: {c}/{a}  {bar}")
    missed = {}
    for q, ok in results:
        if not ok:
            missed[q["concept"]] = missed.get(q["concept"], 0) + 1
    if missed:
        worst = sorted(missed.items(), key=lambda kv: -kv[1])[:3]
        print("  Review next: " + "; ".join(
            f"{CONCEPTS[c]['name']} (§{CONCEPTS[c]['ref']})" for c, _m in worst))
        print(dim("  These concepts are now weighted more heavily in your "
                  "future drills."))
    else:
        print(green("  Clean sweep — these concepts will appear a little "
                    "less often now."))
    print()

def show_stats(st):
    if not st:
        print(dim("No drill history yet — run `quiz` or `sql` first."))
        return
    print(bold("Mastery by concept") +
          dim("  (drives what the quiz asks you next)"))
    rows = []
    for cid, d in st.items():
        if cid not in CONCEPTS or d["a"] == 0:
            continue
        c = CONCEPTS[cid]
        pct = 100.0 * d["c"] / d["a"]
        rows.append((c["ch"], c["ref"], c["name"], d["c"], d["a"], pct))
    rows.sort(key=lambda r: (r[0], r[1]))
    cur_ch = None
    for ch, ref, name, c, a, pct in rows:
        if ch != cur_ch:
            print(bold(f"  Chapter {ch}"))
            cur_ch = ch
        filled = int(round(pct / 10))
        bar = "█" * filled + "░" * (10 - filled)
        colr = green if pct >= 80 else (yellow if pct >= 60 else red)
        print(f"    §{ref:<9} {name:<38} {colr(bar)} {c}/{a}")
    weak = sorted((r for r in rows if r[4] >= 2), key=lambda r: r[5])[:3]
    if weak:
        print(bold("  Weakest right now: ") + "; ".join(
            f"{w[2]} (§{w[1]})" for w in weak))


# ---------------------------------------------------------------------------
# Interactive playground (REPL)
# ---------------------------------------------------------------------------

HELP = """
Playground — type MySQL statements ending with ;
  SHOW DATABASES; / SHOW TABLES; / DESCRIBE Horse; / SHOW CREATE TABLE Movie;
  USE movies;   CREATE DATABASE mydb;   plus SELECT / INSERT / UPDATE /
  DELETE / CREATE TABLE / ALTER TABLE / CREATE VIEW / CREATE INDEX / ...

Study commands (no semicolon needed)
  quiz [n]          exam-style multiple-choice drill (default 10), weighted
                    like the real OA and toward YOUR weak spots
  sql [n]           hands-on SQL-writing drill, graded live (default 5)
  drill <topic> [n] focus a drill: a chapter number (1-5) or a keyword —
                    e.g.  drill joins   drill normal   drill 4   drill keys
  stats             your mastery map by concept
  stats reset       wipe drill history

Sandbox commands
  dbs               list databases        tables      list tables here
  schema <table>    same as DESCRIBE      use <db>    switch database
  reset [db]        restore sample database(s) to original state
  clear             clear the screen      help        this text
  quit              exit

The four sample databases:
  stable   Horse / Student / LessonSchedule   (the chapter 2 & 3 lab tables)
  movies   Movie / Streaming                  (office-hours DDL drills)
  world    Country / City / CountryLanguage   (chapter 3 query examples)
  company  Employee / Department              (DML drills & self-joins)
"""

BANNER = r"""
  ____  _  _  ___   __     ____   ___  _      ____                 _ _
 |  _ \| || ||__ \ / /_   / ___| / _ \| |    / ___|  __ _ _ __   __| | |__   _____  __
 | | | | || |_ / /| '_ \  \___ \| | | | |    \___ \ / _` | '_ \ / _` | '_ \ / _ \ \/ /
 | |_| |__   _/ /_| (_) |  ___) | |_| | |___  ___) | (_| | | | | (_| | |_) | (_) >  <
 |____/   |_||____|\___/  |____/ \__\_\_____||____/ \__,_|_| |_|\__,_|_.__/ \___/_/\_\
"""

def repl(engine, st):
    try:
        import readline
        os.makedirs(APP_DIR, exist_ok=True)
        try:
            readline.read_history_file(HIST_PATH)
        except Exception:
            pass
        import atexit
        atexit.register(lambda: _safe_hist(readline))
    except ImportError:
        pass
    print(cyan(BANNER))
    print(bold("  D426 SQL Sandbox ") + dim(f"v{VERSION}") +
          "  ·  MySQL-flavored playground + adaptive exam drills")
    print(dim("  Blueprint from the D426 practice test: SQL 38% · ER 24% · "
              "normal forms 21% · concepts 14% · physical 3%"))
    print("  Type " + bold("help") + " for commands, " + bold("quiz") +
          " to start drilling, or just write SQL ending with ;")
    print(dim(f"  Current database: {engine.current}   (try: SHOW TABLES;)\n"))
    buf = ""
    while True:
        try:
            prompt = (green(f"{engine.current}> ") if not buf
                      else green("      -> "))
            line = input(prompt)
        except KeyboardInterrupt:
            print("^C" + (dim("  (input cleared)") if buf else ""))
            buf = ""
            continue
        except EOFError:
            print()
            break
        if not buf:
            try:
                if _command(line, engine, st):
                    continue
            except EOFError:
                print()
                break
            if not line.strip():
                continue
        buf += ("\n" if buf else "") + line
        if _statement_complete(buf):
            for stmt in split_statements(buf):
                engine.execute(stmt)
            buf = ""
    save_stats(st)
    print(dim("Bye — stats saved. The OA is heavily definition-based; "
              "keep drilling those §refs."))

def _safe_hist(readline):
    try:
        readline.write_history_file(HIST_PATH)
    except Exception:
        pass

def _command(line, engine, st):
    """Handle bare study/sandbox commands. Returns True if handled."""
    w = line.strip().rstrip(";").strip()
    if not w:
        return False
    parts = w.split()
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd in ("help", "?"):
        print(HELP)
        return True
    if cmd in ("quit", "exit", "q", "\\q"):
        raise EOFError
    if cmd == "clear":
        os.system("clear" if os.name != "nt" else "cls")
        return True
    if cmd == "quiz":
        n = int(args[0]) if args and args[0].isdigit() else 10
        run_quiz(st, n=max(1, min(n, 40)), mode="mcq")
        return True
    if cmd == "sql":
        n = int(args[0]) if args and args[0].isdigit() else 5
        run_quiz(st, n=max(1, min(n, 22)), mode="sql")
        return True
    if cmd == "drill":
        if not args:
            print(yellow("Usage: drill <topic> [n] — e.g. drill joins 8, "
                         "drill 4, drill normal"))
            return True
        n = 8
        if args[-1].isdigit() and len(args) > 1:
            n = int(args[-1]); args = args[:-1]
        topic = " ".join(args)
        mode = "sql" if topic.lower() in ("sql", "hands-on") else "mcq"
        run_quiz(st, n=max(1, min(n, 40)),
                 mode=mode, topic=None if mode == "sql" else topic)
        return True
    if cmd == "stats":
        if args and args[0].lower() == "reset":
            save_stats({})
            st.clear()
            print(dim("Drill history cleared."))
        else:
            show_stats(st)
        return True
    if cmd == "dbs":
        engine.execute("SHOW DATABASES")
        return True
    if cmd == "tables":
        engine.execute("SHOW TABLES")
        return True
    if cmd == "schema" and args:
        engine.execute("DESCRIBE " + args[0])
        return True
    if cmd == "use" and args:
        engine.execute("USE " + args[0])
        return True
    if cmd == "reset":
        try:
            engine.reset(args[0] if args else None)
            print(dim(("Database '" + args[0] + "'" if args else
                       "All sample databases") + " restored to original state."))
        except ValueError as e:
            print(red("ERROR: ") + str(e))
        return True
    return False

# ---------------------------------------------------------------------------
# Optional: pass statements through to a REAL MySQL server
# ---------------------------------------------------------------------------

def mysql_repl(args):
    try:
        import pymysql
    except ImportError:
        print(red("The --mysql mode needs the PyMySQL package:"))
        print("    pip install pymysql")
        print("Everything else in this sandbox works without it.")
        return 1
    import getpass
    pw = args.password if args.password is not None else \
        getpass.getpass(f"Password for {args.user}@{args.host}: ")
    conn = pymysql.connect(host=args.host, port=args.port, user=args.user,
                           password=pw, database=args.database or None)
    print(dim(f"Connected to real MySQL at {args.host}:{args.port} — "
              "statements pass through untranslated. `quit` to exit."))
    buf = ""
    while True:
        try:
            line = input(green("mysql> ") if not buf else green("   -> "))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not buf and line.strip().rstrip(";").lower() in ("quit", "exit", "q"):
            break
        buf += ("\n" if buf else "") + line
        if not buf.rstrip().endswith(";"):
            continue
        try:
            with conn.cursor() as cur:
                cur.execute(buf)
                if cur.description:
                    print_result([d[0] for d in cur.description],
                                 list(cur.fetchall()))
                else:
                    conn.commit()
                    print(dim(f"Query OK, {cur.rowcount} rows affected"))
        except Exception as e:
            print(red("ERROR: ") + str(e))
        buf = ""
    conn.close()
    return 0

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(pack=None, data_dir=None, argv=None):
    if pack is not None:
        init(pack, data_dir)
    ap = argparse.ArgumentParser(
        prog="d426_sandbox.py",
        description="MySQL-flavored SQL playground + adaptive exam drills "
                    "for WGU D426.")
    ap.add_argument("--quiz", type=int, nargs="?", const=10, metavar="N",
                    help="run an N-question exam-style drill and exit")
    ap.add_argument("--sql", type=int, nargs="?", const=5, metavar="N",
                    help="run an N-task hands-on SQL drill and exit")
    ap.add_argument("--drill", metavar="TOPIC",
                    help="focus the drill on a chapter (1-5) or keyword")
    ap.add_argument("--stats", action="store_true", help="show mastery map")
    ap.add_argument("--reset", action="store_true",
                    help="restore all sample databases")
    ap.add_argument("--seed", type=int, help="seed the question randomizer")
    ap.add_argument("--mysql", action="store_true",
                    help="pass statements to a real MySQL server instead")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="root")
    ap.add_argument("--password", default=None)
    ap.add_argument("--database", default=None)
    ap.add_argument("--version", action="version",
                    version=f"D426 SQL Sandbox v{VERSION}")
    args = ap.parse_args(argv)
    if not SAMPLE_DBS and not (getattr(args, 'quiz', None) or getattr(args, 'sql', None) or getattr(args, 'stats', False)):
        print('This course has no SQL data for the terminal REPL \u2014 use --quiz N, --sql N, or --stats here; the web app has its playground.')
        return 0
    if args.mysql:
        return mysql_repl(args)

    rng = random.Random(args.seed) if args.seed is not None else random.Random()
    st = load_stats()
    if args.stats:
        show_stats(st)
        return 0
    engine = Engine(APP_DIR, SAMPLE_DBS, DB_DESCRIPTIONS)
    if args.reset:
        engine.reset()
        print(dim("All sample databases restored."))
        return 0
    if args.quiz is not None:
        run_quiz(st, n=args.quiz, mode="mcq", topic=args.drill, rng=rng)
        return 0
    if args.sql is not None:
        run_quiz(st, n=args.sql, mode="sql", topic=None, rng=rng)
        return 0
    if args.drill:
        run_quiz(st, n=8, mode="mcq", topic=args.drill, rng=rng)
        return 0
    repl(engine, st)
    return 0


