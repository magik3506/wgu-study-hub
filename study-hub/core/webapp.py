"""WGU Study Hub web layer — serves every discovered course pack.
The frontend is a React app built into core/webdist/ (see web/); this
server serves those static files plus JSON APIs. The homepage reads
/api/courses; each course app at /c/<slug> reads /c/<slug>/api/meta and
renders tabs driven by pack capabilities (Playground/SQL drill only when
stipulated, Study guide tab when courses/<slug>/study_guide.pdf exists).
Mascot voice lines live OUTSIDE the build, in <repo>/assets/ — served
read-only under /media/ so adding lines never requires an npm build."""
import json
import os
import random
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlparse

from . import quiz as Q
from ._assets import FALLBACK_HTML
from .packs import data_dir_for

MAX_SESSIONS = 24
STATE = {}          # slug -> course state dict

WEBDIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webdist")
# User-managed media (mascot voice lines etc.): <repo>/assets/, served at
# /media/. Keeping audio out of web/public means dropping in new files is
# all it takes — no rebuild, and vite's emptyOutDir can't eat them.
ASSETS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "assets")

AUDIO_EXTS = (".mp3", ".wav", ".ogg", ".m4a", ".webm")


def voiceline_manifest():
    """assets/voicelines/<type>/*  →  {type: [/media/... urls]}.

    The frontend asks for this once at boot and plays whatever is actually
    on disk — any file names, any count, any audio extension. Renaming,
    adding, or removing lines never needs a code change."""
    root = os.path.join(ASSETS, "voicelines")
    out = {}
    if not os.path.isdir(root):
        return out
    for t in sorted(os.listdir(root)):
        d = os.path.join(root, t)
        if not os.path.isdir(d) or t.startswith("."):
            continue
        files = sorted(f for f in os.listdir(d)
                       if f.lower().endswith(AUDIO_EXTS)
                       and not f.startswith("."))
        if files:
            out[t] = ["/media/voicelines/%s/%s" % (quote(t), quote(f))
                      for f in files]
    return out

MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript",
        ".css": "text/css; charset=utf-8", ".json": "application/json",
        ".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp",
        ".ico": "image/x-icon", ".pdf": "application/pdf",
        ".woff2": "font/woff2", ".woff": "font/woff", ".txt": "text/plain",
        ".map": "application/json",
        ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
        ".m4a": "audio/mp4", ".webm": "audio/webm"}

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
# payloads the React app renders from
# ---------------------------------------------------------------------------

def _planned():
    from .packs import COURSES_ROOT
    try:
        with open(os.path.join(COURSES_ROOT, "planned.json")) as f:
            return json.load(f)
    except Exception:
        return []

def pack_chips(p):
    """Capability chips, single source of truth for cards."""
    chips = ["Exam drill", "Mastery"]
    if p.has_playground:
        chips.insert(0, p.playground.label)
    if p.sql_generators:
        chips.insert(-1, "SQL drill")
    if p.study_guide_path:
        chips.append("Study guide")
    return chips

def home_payload():
    courses = []
    for st in STATE.values():
        p = st["pack"]
        courses.append({"slug": p.slug, "code": p.code, "name": p.name,
                        "blurb": p.blurb, "chips": pack_chips(p)})
    have = {st["pack"].code for st in STATE.values()}
    planned = [c for c in _planned() if c.get("code") not in have]
    return {"courses": courses, "planned": planned}

def course_tabs(p):
    tabs = []
    if p.has_playground:
        tabs.append({"id": "playground", "label": "Playground"})
    tabs.append({"id": "drill", "label": "Exam drill"})
    if p.sql_generators:
        tabs.append({"id": "sqldrill", "label": "SQL drill"})
    tabs.append({"id": "mastery", "label": "Mastery"})
    tabs.append({"id": "guide", "label": "Study guide"})
    return tabs

def course_meta(p):
    """Everything the course page needs to render capability-true UI."""
    pg = None
    if p.has_playground:
        pg = {"label": p.playground.label,
              "placeholder": p.playground.placeholder,
              "stdin": bool(getattr(p.playground, "stdin_enabled", False))}
    return {"slug": p.slug, "code": p.code, "name": p.name,
            "badge": p.badge, "base": "/c/" + p.slug,
            "tabs": course_tabs(p),
            "unit_label": p.unit_label,
            "chapters": [{"ch": ch, "name": p.chapter_names.get(ch, "")}
                         for ch in sorted(p.ch_weight)],
            "topics": [{"value": v, "label": l} for v, l in p.topics],
            "playground": pg,
            "has_sql_drill": bool(p.sql_generators),
            "guide": bool(p.study_guide_path)}

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

def _index_bytes():
    try:
        with open(os.path.join(WEBDIST, "index.html"), "rb") as f:
            return f.read()
    except OSError:
        return FALLBACK_HTML.encode("utf-8")

class Handler(BaseHTTPRequestHandler):
    server_version = "WGUStudyHub/3.1"

    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype, cache="no-store"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj), "application/json")

    def _index(self):
        self._send(200, _index_bytes(), "text/html; charset=utf-8")

    def _static(self, path):
        """Serve a file from webdist. Returns True if it existed."""
        rel = os.path.normpath(path.lstrip("/"))
        if rel.startswith("..") or os.path.isabs(rel):
            return False
        full = os.path.join(WEBDIST, rel)
        if not (os.path.isfile(full)
                and os.path.realpath(full).startswith(
                    os.path.realpath(WEBDIST) + os.sep)):
            return False
        ext = os.path.splitext(full)[1].lower()
        # Vite content-hashes everything under /assets — cache those hard.
        cache = ("public, max-age=31536000, immutable"
                 if rel.startswith("assets" + os.sep) else "no-store")
        with open(full, "rb") as f:
            self._send(200, f.read(),
                       MIME.get(ext, "application/octet-stream"), cache)
        return True

    def _media(self, path):
        """Serve /media/<rel> from <repo>/assets/<rel> (read-only, jailed).
        Voice lines live at assets/voicelines/<event>/ under any file names
        (see voiceline_manifest) — no build step involved."""
        rel = os.path.normpath(unquote(path[len("/media/"):]))
        if rel.startswith("..") or os.path.isabs(rel):
            return False
        full = os.path.join(ASSETS, rel)
        if not (os.path.isfile(full)
                and os.path.realpath(full).startswith(
                    os.path.realpath(ASSETS) + os.sep)):
            return False
        ext = os.path.splitext(full)[1].lower()
        with open(full, "rb") as f:
            self._send(200, f.read(),
                       MIME.get(ext, "application/octet-stream"),
                       "public, max-age=3600")
        return True

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
                    return self._index()
                if rest == "/api/courses":
                    return self._json(home_payload())
                if rest == "/api/voicelines":
                    return self._json(voiceline_manifest())
                if rest.startswith("/media/") and self._media(rest):
                    return
                if self._static(rest):
                    return
            else:
                if rest == "":
                    return self._index()
                if rest == "api/meta":
                    return self._json(course_meta(st["pack"]))
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
            else:
                if rest == "/api/shutdown":
                    # The web UI's power button (and `--stop`). Reply first,
                    # then ask the serve_forever loop to wind down.
                    self._json({"ok": True,
                                "bye": "Rest well, night owl."})
                    t = threading.Timer(0.2, self.server.shutdown)
                    t.daemon = True
                    t.start()
                    return
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
          "Stop it with the \u23fb button")
    print("      in the app's top bar, or Ctrl+C here.")
    print()
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
        # serve_forever only returns after /api/shutdown (power button
        # or `wgu_study_hub.py --stop`).
        print("\n  Stopped from the app. Go get some sleep, night owl.")
    except KeyboardInterrupt:
        print("\n  Stopped. Go get some sleep, night owl.")
