"""WGU Study Hub web layer — serves every discovered course pack.
Homepage lists packs; each gets its own app at /c/<slug> with tabs driven
by pack capabilities (Playground/SQL drill only for SQL courses, Study
guide tab embedding courses/<slug>/study_guide.pdf when present)."""
import json
import random
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import quiz as Q
from ._assets import (APP_CSS, COURSE_TMPL, FAVICON, HOME_TMPL, OWL_SVG,
                      PLAYGROUND_SECTION, SQLDRILL_SECTION)
from .packs import data_dir_for

MAX_SESSIONS = 24
STATE = {}          # slug -> course state dict

PLANNED = [
    {"code": "D427", "name": "Data Management \u2014 Applications",
     "blurb": "The SQL-writing course. This hub has a perch reserved for it."},
]

def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

def _jval(v):
    if v is None or isinstance(v, (int, float, str)):
        return v
    return str(v)

def rows_json(rows, cap=500):
    out = [[_jval(v) for v in r] for r in rows[:cap]]
    return out, len(rows), len(rows) > cap

def build_state(pack):
    dd = data_dir_for(pack.slug)
    pg = pack.playground if pack.has_playground else None
    if pg:
        pg.bind(dd)
    return {"pack": pack, "pg": pg, "dir": dd,
            "stats": Q.load_stats(Q.os.path.join(dd, "stats.json")),
            "stats_path": Q.os.path.join(dd, "stats.json"),
            "lock": threading.RLock(), "sessions": {}}

# ---------------------------------------------------------------------------
# page rendering
# ---------------------------------------------------------------------------

def _planned():
    import os
    from .packs import COURSES_ROOT
    try:
        with open(os.path.join(COURSES_ROOT, "planned.json")) as f:
            return json.load(f)
    except Exception:
        return PLANNED

def home_html():
    cards = []
    for st in STATE.values():
        p = st["pack"]
        code = _esc(p.code)
        codehtml = f"{code[0]}<b>{code[1:]}</b>" if len(code) > 1 else code
        chips = ["Exam drill", "Mastery"]
        if p.has_playground:
            chips.insert(0, p.playground.label)
        if p.sql_generators:
            chips.insert(-1, "SQL drill")
        if p.study_guide_path:
            chips.append("Study guide")
        chiph = "".join(f'<span class="chip">{c}</span>' for c in chips)
        cards.append(f'''    <a class="course" href="/c/{_esc(p.slug)}">
      <span class="pill">READY</span>
      <div class="code">{codehtml}</div>
      <h2>{_esc(p.name)}</h2>
      <p>{_esc(p.blurb)}</p>
      <div class="chiprow">{chiph}</div>
    </a>''')
    have = {st["pack"].code for st in STATE.values()}
    for c in _planned():
        if c["code"] in have:
            continue
        code = _esc(c["code"])
        codehtml = f"{code[0]}<b>{code[1:]}</b>"
        cards.append(f'''    <div class="course planned" aria-disabled="true">
      <span class="pill dim">PLANNED</span>
      <div class="code">{codehtml}</div>
      <h2>{_esc(c["name"])}</h2>
      <p>{_esc(c["blurb"])}</p>
    </div>''')
    return (HOME_TMPL.replace("%%CARDS%%", "\n".join(cards))
            .replace("%%OWL%%", OWL_SVG).replace("%%FAVICON%%", FAVICON))

def course_html(st):
    p = st["pack"]
    tabs = []
    if p.has_playground:
        tabs.append(("playground", "Playground"))
    tabs.append(("drill", "Exam drill"))
    if p.sql_generators:
        tabs.append(("sqldrill", "SQL drill"))
    tabs.append(("mastery", "Mastery"))
    tabs.append(("guide", "Study guide"))
    tabh = "\n".join(
        f'  <button class="tab{" on" if i == 0 else ""}" data-tab="{t}">'
        f"{lbl}</button>" for i, (t, lbl) in enumerate(tabs))

    opts = ['<option value="">Everything (blueprint-weighted)</option>']
    for ch in sorted(p.ch_weight):
        nm = p.chapter_names.get(ch, "")
        opts.append(f'<option value="{ch}">{_esc(p.unit_label)} {ch}'
                    + (f" &middot; {_esc(nm)}" if nm else "") + "</option>")
    for val, lbl in p.topics:
        opts.append(f'<option value="{_esc(val)}">{_esc(lbl)}</option>')

    if p.study_guide_path:
        guide = ('<h3>Study guide</h3><p class="sub">The exam-oriented '
                 'reference built from the course source.</p>'
                 '<div style="border:1px solid var(--line);border-radius:10px;'
                 'overflow:hidden;height:78vh"><embed src="%%BASE%%/guide.pdf" '
                 'type="application/pdf" style="width:100%;height:100%">'
                 '</div><p class="sub" style="margin-top:10px">'
                 '<a href="%%BASE%%/guide.pdf" download>Download PDF</a></p>')
    else:
        guide = ('<h3>Study guide</h3><div class="empty">No study guide in '
                 'this pack yet.<br><br>Generate one with the '
                 '<span class="mono">course-study-guide</span> skill, then '
                 'drop the PDF at <span class="mono">courses/'
                 + _esc(p.slug) + '/study_guide.pdf</span> and refresh.</div>')

    return (COURSE_TMPL
            .replace("%%PLAYGROUND_SECTION%%",
                     PLAYGROUND_SECTION if p.has_playground else "")
            .replace("%%PG_LABEL%%",
                     _esc(p.playground.label) if p.has_playground else "")
            .replace("%%PG_PLACEHOLDER%%",
                     _esc(p.playground.placeholder)
                     if p.has_playground else "")
            .replace("%%PG_STDIN_CLASS%%",
                     ("" if getattr(p.playground, "stdin_enabled", False)
                      else "hidden") if p.has_playground else "hidden")
            .replace("%%SQLDRILL_SECTION%%",
                     SQLDRILL_SECTION if p.sql_generators else "")
            .replace("%%TABS%%", tabh)
            .replace("%%TOPIC_OPTIONS%%", "\n        ".join(opts))
            .replace("%%GUIDE_BODY%%", guide)
            .replace("%%BASE%%", "/c/" + p.slug)
            .replace("%%CODE%%", _esc(p.code))
            .replace("%%NAME%%", _esc(p.name))
            .replace("%%BADGE%%", _esc(p.badge)))

# ---------------------------------------------------------------------------
# APIs (per course state)
# ---------------------------------------------------------------------------


def api_run(st, body):
    with st["lock"]:
        return st["pg"].run(str(body.get("source", "")),
                            str(body.get("stdin", "")))

def api_side(st):
    with st["lock"]:
        return {"sidebar": st["pg"].sidebar(),
                "selector": st["pg"].selector()}

def api_reset(st, body):
    with st["lock"]:
        return {"ok": True, "message": st["pg"].reset(body.get("target"))}

def _question_payload(st, sess):
    p = st["pack"]
    i = sess["i"]
    q = sess["qs"][i]
    c = p.concepts[q["concept"]]
    out = {"index": i + 1, "total": len(sess["qs"]),
           "tag": f"Ch{c['ch']} \u00a7{c['ref']} \u00b7 {c['name']}",
           "prompt": q["prompt"]}
    if q["type"] == "tf":
        out["qtype"] = "mcq"
        out["options"] = ["True", "False"]
    elif q["type"] == "mcq":
        out["qtype"] = "mcq"
        out["options"] = [str(o) for o in q["options"]]
    else:
        out["qtype"] = "sql"
        out["db"] = q["db"]
        out["kind"] = q["kind"]
        out["tables"] = Q._scratch_tables(sess["ctx"], q["db"])
        out["has_hint"] = bool(q.get("hint"))
    return out

def api_quiz_start(st, body):
    p = st["pack"]
    mode = "sql" if body.get("mode") == "sql" else "mcq"
    if mode == "sql" and not p.sql_generators:
        return None
    try:
        n = int(body.get("n") or (10 if mode == "mcq" else 5))
    except (TypeError, ValueError):
        n = 10
    n = max(1, min(n, 40))
    topic = (str(body.get("topic") or "")).strip() or None
    seed = body.get("seed")
    rng = random.Random(seed) if seed is not None else random.Random()
    ctx = Q.QuizContext(p.sample_dbs)
    with st["lock"]:
        snapshot = json.loads(json.dumps(st["stats"])) if st["stats"] else {}
    source = p.mcq_generators if mode == "mcq" else p.sql_generators
    qs = Q.pick_questions(n, snapshot, rng, ctx, source, p.concepts,
                          p.ch_weight, topic if mode == "mcq" else None)
    if not qs:
        return None
    sid = secrets.token_hex(8)
    while len(st["sessions"]) >= MAX_SESSIONS:
        st["sessions"].pop(next(iter(st["sessions"])))
    st["sessions"][sid] = {"qs": qs, "i": 0, "results": [], "ctx": ctx,
                           "mode": mode}
    return {"session": sid, "mode": mode, "total": len(qs),
            "question": _question_payload(st, st["sessions"][sid])}

def _summary(st, sess):
    p = st["pack"]
    n = len(sess["results"])
    right = sum(1 for _c, ok in sess["results"] if ok)
    by = {}
    for cid, ok in sess["results"]:
        ch = p.concepts[cid]["ch"]
        a, c = by.get(ch, (0, 0))
        by[ch] = (a + 1, c + (1 if ok else 0))
    missed = {}
    for cid, ok in sess["results"]:
        if not ok:
            missed[cid] = missed.get(cid, 0) + 1
    weak = [{"name": p.concepts[c]["name"], "ref": p.concepts[c]["ref"]}
            for c, _m in sorted(missed.items(), key=lambda kv: -kv[1])[:3]]
    return {"score": right, "total": n,
            "pct": round(100.0 * right / max(n, 1)),
            "chapters": [{"ch": ch, "attempts": a, "correct": c}
                         for ch, (a, c) in sorted(by.items())],
            "weak": weak}

def api_quiz_answer(st, body):
    sess = st["sessions"].get(str(body.get("session") or ""))
    if not sess or sess["i"] >= len(sess["qs"]):
        return {"error": "That drill session has ended \u2014 start a new "
                         "one."}, 410
    q = sess["qs"][sess["i"]]
    action = body.get("action")
    if action == "hint":
        return {"hint": q.get("hint") or "No hint for this one \u2014 trust "
                                         "the schema and the prompt."}, 200
    out = {}
    if action == "skip":
        ok = False
        out["skipped"] = True
    elif q["type"] in ("mcq", "tf"):
        try:
            idx = int(body.get("answer"))
        except (TypeError, ValueError):
            idx = -1
        ans = (0 if q["answer"] else 1) if q["type"] == "tf" else q["answer"]
        ok = idx == ans
    else:
        ok, fb = Q.check_sql_task(q, str(body.get("answer") or ""),
                                  sess["ctx"])
        out["feedback"] = fb
    out["correct"] = bool(ok)
    if q["type"] in ("mcq", "tf"):
        opts = (["True", "False"] if q["type"] == "tf"
                else [str(o) for o in q["options"]])
        ansidx = (0 if q["answer"] else 1) if q["type"] == "tf" else q["answer"]
        out["correct_index"] = ansidx
        out["correct_text"] = opts[ansidx]
        out["explain"] = q["explain"]
    else:
        out["reference"] = q["reference"] + ";"
        if q["kind"] == "select" and not ok:
            try:
                h, r = sess["ctx"].q(q["db"], q["reference"])
                rj, total, _t = rows_json(r, 8)
                out["expected"] = {"headers": h, "rows": rj, "total": total}
            except Exception:
                pass
    with st["lock"]:
        Q.record_result(st["stats"], q["concept"], bool(ok))
        Q.save_stats(st["stats"], st["stats_path"])
    sess["results"].append((q["concept"], bool(ok)))
    sess["i"] += 1
    if sess["i"] < len(sess["qs"]):
        out["next"] = _question_payload(st, sess)
    else:
        out["summary"] = _summary(st, sess)
    return out, 200

def api_stats(st):
    p = st["pack"]
    with st["lock"]:
        data = json.loads(json.dumps(st["stats"])) if st["stats"] else {}
    rows = []
    for cid, d in data.items():
        if cid not in p.concepts or not d.get("a"):
            continue
        c = p.concepts[cid]
        rows.append({"ch": c["ch"], "ref": c["ref"], "name": c["name"],
                     "correct": d["c"], "attempts": d["a"],
                     "pct": round(100.0 * d["c"] / d["a"])})
    rows.sort(key=lambda r: (r["ch"], r["ref"]))
    weak = sorted([r for r in rows if r["attempts"] >= 2],
                  key=lambda r: r["pct"])[:3]
    return {"concepts": rows, "weak": weak,
            "blueprint": [{"ch": k, "w": round(v * 100)}
                          for k, v in sorted(p.ch_weight.items())]}

# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "WGUStudyHub/2.0"

    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj), "application/json")

    def _read_body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def _route(self):
        parts = urlparse(self.path).path.split("/")
        if len(parts) >= 3 and parts[1] == "c" and parts[2] in STATE:
            return STATE[parts[2]], "/".join(parts[3:])
        return None, urlparse(self.path).path

    def do_GET(self):
        st, rest = self._route()
        try:
            if st is None:
                if rest == "/":
                    return self._send(200, home_html(),
                                      "text/html; charset=utf-8")
                if rest == "/app.css":
                    return self._send(200, APP_CSS, "text/css; charset=utf-8")
            else:
                if rest == "":
                    return self._send(200, course_html(st),
                                      "text/html; charset=utf-8")
                if rest == "guide.pdf" and st["pack"].study_guide_path:
                    with open(st["pack"].study_guide_path, "rb") as f:
                        return self._send(200, f.read(), "application/pdf")
                if rest == "api/side" and st["pg"]:
                    return self._json(api_side(st))
                if rest == "api/stats":
                    return self._json(api_stats(st))
        except Exception as e:
            return self._json({"error": str(e)}, 500)
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        st, rest = self._route()
        body = self._read_body()
        try:
            if st is not None:
                if rest == "api/run" and st["pg"]:
                    return self._json(api_run(st, body))
                if rest == "api/reset" and st["pg"]:
                    try:
                        return self._json(api_reset(st, body))
                    except ValueError as e:
                        return self._json({"error": str(e)}, 400)
                if rest == "api/quiz/start":
                    s = api_quiz_start(st, body)
                    if s is None:
                        return self._json(
                            {"error": "No questions matched that topic."}, 400)
                    return self._json(s)
                if rest == "api/quiz/answer":
                    out, code = api_quiz_answer(st, body)
                    return self._json(out, code)
                if rest == "api/stats/reset":
                    with st["lock"]:
                        st["stats"].clear()
                        Q.save_stats(st["stats"], st["stats_path"])
                    return self._json({"ok": True})
        except Exception as e:
            return self._json({"error": str(e)}, 500)
        self._json({"error": "not found"}, 404)

# ---------------------------------------------------------------------------
# serve
# ---------------------------------------------------------------------------

def serve(packs, port=8426, open_browser=True):
    for p in packs:
        STATE[p.slug] = build_state(p)
    httpd = None
    for cand in range(port, port + 20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", cand), Handler)
            port = cand
            break
        except OSError:
            continue
    if httpd is None:
        raise SystemExit(f"No free port found near {port}.")
    url = f"http://127.0.0.1:{port}/"
    print()
    print("  \U0001F989  WGU Study Hub is up")
    print(f"      {url}")
    print("      Courses: " + (", ".join(p.code for p in packs)
          or "(none yet \u2014 drop a <slug>-pack.zip into courses/ "
             "and restart)"))
    print("      Progress lives in ~/.wgu_study_hub (shared with --cli). "
          "Ctrl+C stops the server.")
    print()
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. Go get some sleep, night owl.")
