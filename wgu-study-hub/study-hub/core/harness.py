"""Pack validator — the comprehensive quality gate every course must pass.

Converts judgment into enforcement. Checks are grouped:
  framework   assets/webapp import, template JS bind hygiene
  manifest    payload fields, blueprint, chapter names, topics, imports
  questions   types, content lint (repr/format/mojibake/placeholder leaks),
              answer leaks, shuffle-hostile options, duplicates, lengths
  determinism same-seed purity, seed variety, cross-process fingerprint
  sql tasks   reference self-grading, answerability, junk rejection,
              reference determinism, content lint
  playground  stipulation, selfchecks, garbage-input resilience
  selection   pick_questions integration, every topic + chapter reachable
  render      course page tokens, capability-true markup, node JS execution
ERRORS fail the pack. WARNINGS print for human review and do not fail.
Run via:  python3 wgu_study_hub.py --selftest [slug|all]
"""
import hashlib
import json
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from .quiz import QuizContext, check_sql_task, pick_questions, _topic_match

MCQ_SEEDS = 5
SQL_SEEDS = 8
FP_SEEDS = 3
def _is_child():
    return os.environ.get("WGU_HARNESS_CHILD") == "1"

def _seed(name, mult, s):
    return sum(name.encode()) * mult + s          # stable across processes

# ---------------------------------------------------------------------------
# content lint
# ---------------------------------------------------------------------------

_TUPLE_REPR = re.compile(r"[(\[]\s*'[^']{0,80}'\s*,\s*'")
_TUPLE_REPR2 = re.compile(r'[(\[]\s*"[^"]{0,80}"\s*,\s*"')
_SQL_CTX = re.compile(r"\b(?:in|values)\s*\($", re.I)
_FMT_BRACE = re.compile(r"\{[A-Za-z_]\w*\}")
_FMT_PCT = re.compile(r"%[sdr]\b")
_ESC_UNI = re.compile(r"\\u[0-9a-fA-F]{4}")
_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|TBD|XXX|PLACEHOLDER)\b")
_LOREM = re.compile(r"lorem ipsum", re.I)
_MOJIBAKE = ("\ufffd", "\u00e2\u20ac", "\u00c3\u00a9", "\u00c2\u00a0")

def lint_text(val, where, errs, mode=None):
    """Content-sanity lint. mode='code' skips pattern lints for questions
    that intentionally display raw code (set q['lint']='code')."""
    if not isinstance(val, str):
        errs.append(f"{where}: not a string ({type(val).__name__}) "
                    "\u2014 raw Python object leaked into content")
        return
    s = val
    if not s.strip():
        errs.append(f"{where}: empty/whitespace")
        return
    for m in _MOJIBAKE:
        if m in s:
            errs.append(f"{where}: encoding artifact {m!r}")
            return
    m = re.search(r"%%[A-Za-z_]+%%", s)
    if m:
        errs.append(f"{where}: unreplaced template token {m.group()!r}")
    if _PLACEHOLDER.search(s) or _LOREM.search(s):
        errs.append(f"{where}: dev placeholder marker left in: {s[:60]!r}")
    if mode == "code":
        return
    for pat in (_TUPLE_REPR, _TUPLE_REPR2):
        m = pat.search(s)
        if m and (m.start() == 0 or not (s[m.start() - 1].isalnum()
                                         or s[m.start() - 1] == "_")) \
                and not _SQL_CTX.search(s[max(0, m.start() - 10):
                                          m.start() + 1]):
            errs.append(f"{where}: tuple/list repr leaked into text: "
                        f"...{s[max(0, m.start() - 15):m.start() + 40]!r}...")
            break
    for sig in ("<function ", " object at 0x", "<class '", "dict_keys(",
                "dict_values(", "<__main__"):
        if sig in s:
            errs.append(f"{where}: object repr leaked: {sig!r}")
            break
    if _FMT_BRACE.search(s):
        errs.append(f"{where}: unformatted {{placeholder}}: "
                    f"{_FMT_BRACE.search(s).group()!r} in {s[:60]!r}")
    if _FMT_PCT.search(s):
        errs.append(f"{where}: printf-style leftover "
                    f"{_FMT_PCT.search(s).group()!r} in {s[:60]!r}")
    if _ESC_UNI.search(s):
        errs.append(f"{where}: escaped \\uXXXX leaked literally")

_NUMISH = re.compile(r"^[\s\d.,%$+\-*/=()xX^]+$")

def _q_key(q):
    return json.dumps(q, sort_keys=True, default=str)

def check_question(q, gname, s, pack, errs, warns):
    where = f"{gname} (seed {s})"
    mode = q.get("lint")
    if q.get("concept") not in pack.concepts:
        errs.append(f"{where}: unknown concept {q.get('concept')!r}")
        return
    lint_text(q.get("prompt"), where + " prompt", errs, mode)
    lint_text(q.get("explain"), where + " explain", errs, mode)
    if isinstance(q.get("prompt"), str) and len(q["prompt"].strip()) < 15:
        errs.append(f"{where}: prompt too short: {q['prompt']!r}")
    if isinstance(q.get("explain"), str):
        if len(q["explain"].strip()) < 15:
            errs.append(f"{where}: explain too short \u2014 explains teach")
        elif q["explain"].strip() == str(q.get("prompt", "")).strip():
            errs.append(f"{where}: explain merely repeats the prompt")
    if q["type"] == "tf":
        if not isinstance(q.get("answer"), bool):
            errs.append(f"{where}: tf answer must be bool")
        return
    if q["type"] != "mcq":
        errs.append(f"{where}: bad type {q['type']!r}")
        return
    opts = q.get("options")
    if not isinstance(opts, list) or len(opts) < 3:
        errs.append(f"{where}: options must be a list of >=3")
        return
    if len(opts) > 5:
        errs.append(f"{where}: {len(opts)} options \u2014 UI keys support "
                    "A\u2013E (max 5)")
    for i, o in enumerate(opts):
        lint_text(o, f"{where} option {i}", errs, mode)
    if not all(isinstance(o, str) for o in opts):
        return
    norm = [" ".join(o.split()) for o in opts]
    if len(set(norm)) != len(norm):
        errs.append(f"{where}: duplicate options: {opts}")
    if any(len(o) > 300 for o in opts):
        warns.append(f"{where}: option over 300 chars \u2014 leaked "
                     "structure or paragraph?")
    for o in opts:
        if re.search(r"\b(the above|of these|all of the above)\b", o, re.I):
            errs.append(f"{where}: shuffle-hostile option {o!r} \u2014 "
                        "positional phrases break under shuffling")
            break
    a = q.get("answer")
    if not isinstance(a, int) or not (0 <= a < len(opts)):
        errs.append(f"{where}: answer index invalid: {a!r}")
        return
    ans = opts[a].strip()
    if (len(ans) >= 5 and not _NUMISH.match(ans) and len(ans.split()) <= 4
            and isinstance(q.get("prompt"), str)):
        inp = lambda t: re.search(r"(?<![\w])" + re.escape(t.strip())
                                  + r"(?![\w])", q["prompt"])
        if inp(ans) and not any(inp(o) for i, o in enumerate(opts)
                                if i != a):
            errs.append(f"{where}: correct answer {ans!r} appears verbatim "
                        "in the prompt while no distractor does \u2014 "
                        "answer giveaway")

# ---------------------------------------------------------------------------
# fingerprints (cross-process determinism)
# ---------------------------------------------------------------------------

def pack_fingerprint(pack):
    """Per-generator digests \u2014 stable iff generators are pure
    functions of rng (no hash(), set order, globals, time)."""
    ctx = QuizContext(pack.sample_dbs)
    out = {}
    for gen in list(pack.mcq_generators) + list(pack.sql_generators):
        gname = getattr(gen, "__name__", str(gen))
        mult = 7 if gen in pack.mcq_generators else 11
        h = hashlib.sha256()
        for s in range(FP_SEEDS):
            try:
                q = gen(random.Random(_seed(gname, mult, s)), ctx)
                h.update(_q_key(q).encode())
            except Exception as e:
                h.update(f"{gname}:{s}:RAISED:{type(e).__name__}".encode())
        out[gname] = h.hexdigest()
    return out

def _cross_process_fingerprint(pack, errs):
    if _is_child():
        return
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code = ("import sys; sys.path.insert(0, '.');"
            "from core.packs import discover;"
            "from core.harness import pack_fingerprint;"
            f"p=[x for x in discover(include_template=True) "
            f"if x.slug=={pack.slug!r}][0];"
            "import json; print(json.dumps(pack_fingerprint(p)))")
    env = dict(os.environ,
               PYTHONHASHSEED=str((int(os.environ.get(
                   "PYTHONHASHSEED", "0") or "0") + 977) % 4000 + 1),
               WGU_HARNESS_CHILD="1")
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                           capture_output=True, text=True, timeout=180)
        line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        if r.returncode or not line:
            errs.append("cross-process fingerprint child failed: "
                        + (r.stderr or "")[-160:])
        else:
            child = json.loads(line)
            mine = pack_fingerprint(pack)
            diff = sorted(g for g in mine if child.get(g) != mine[g])
            if diff:
                errs.append("generators differ across processes (hash()/"
                            "set-order/global state instead of rng): "
                            + ", ".join(diff[:6])
                            + (" \u2026" if len(diff) > 6 else ""))
    except Exception as e:
        errs.append(f"cross-process fingerprint: {e!r}")

# ---------------------------------------------------------------------------
# framework checks (once)
# ---------------------------------------------------------------------------

_fw_done = False

def _framework(errs):
    global _fw_done
    if _fw_done:
        return
    _fw_done = True
    try:
        from . import webapp, _assets  # corruption lesson: selftest alone
        tmpl = _assets.COURSE_TMPL     # never imports the web layer
        if re.search(r'\n\$\("#\w+"\)\.addEventListener', tmpl):
            errs.append("framework: top-level direct addEventListener in "
                        "template \u2014 use the null-safe bindEl helper")
        pj = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "courses", "planned.json")
        if os.path.exists(pj):
            json.load(open(pj))
    except Exception as e:
        errs.append(f"framework: web layer broken: {e!r}")

# ---------------------------------------------------------------------------
# node shim (opportunistic real JS execution)
# ---------------------------------------------------------------------------

NODE_SHIM = r"""
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
const ids = new Set([...html.matchAll(/id="([A-Za-z]+)"/g)].map(m => m[1]));
const tabs = [...html.matchAll(/<button class="tab[^"]*" data-tab="([a-z]+)"/g)]
  .map(m => ({dataset: {tab: m[1]}, addEventListener(){},
              classList: {add(){}, remove(){}, toggle(){}}}));
function el(id){ return {id, addEventListener(){}, dataset:{}, style:{},
  classList:{add(){},remove(){},toggle(){},contains(){return false}},
  value:"", innerHTML:"", textContent:"", focus(){}, disabled:false,
  appendChild(){}, childNodes:[], closest(){return null},
  querySelector(){return null}, querySelectorAll(){return []}}; }
global.document = {
  querySelector(sel){
    if (sel.startsWith("#")) return ids.has(sel.slice(1)) ? el(sel.slice(1)) : null;
    if (sel === ".play") return html.includes('class="play"') ? el("play") : null;
    return null; },
  querySelectorAll(sel){ return sel === ".tab" ? tabs : []; },
  createElement(){ return el("x"); }, addEventListener(){}, };
global.history = {replaceState(){}}; global.location = {hash: ""};
global.fetch = async () => ({json: async () => ({sidebar:null, selector:null,
  blocks:[], notes:[], concepts:[], weak:[], blueprint:[], results:[]})});
global.confirm = () => false; global.alert = () => {};
process.on("unhandledRejection", e => { console.error("ASYNC:", e && e.message);
  process.exit(1); });
try { eval(script); } catch (e) { console.error("SYNC:", e.message); process.exit(1); }
setTimeout(() => process.exit(0), 60);
"""

def _render_checks(pack, errs, warns):
    try:
        from .webapp import course_html
        html = course_html({"pack": pack})
    except Exception as e:
        errs.append(f"render: course_html raised {e!r}")
        return
    if "%%" in html:
        errs.append("render: unreplaced %% token in page: "
                    + html[html.index("%%") - 20:html.index("%%") + 30])
    want = (["playground"] if pack.has_playground else []) + ["drill"] \
        + (["sqldrill"] if pack.sql_generators else []) + ["mastery", "guide"]
    got = re.findall(r'<button class="tab[^"]*" data-tab="([a-z]+)"', html)
    if got != want:
        errs.append(f"render: tabs {got} != capabilities {want}")
    if pack.has_playground:
        if 'id="playground"' not in html:
            errs.append("render: stipulated playground missing from page")
        cls = 'id="stdinwrap" class="%s"' % (
            "" if getattr(pack.playground, "stdin_enabled", False)
            else "hidden")
        if cls not in html:
            errs.append("render: stdin box visibility wrong for backend")
    elif 'id="playground"' in html or "console" in html.split("<script>")[0]:
        errs.append("render: console markup on a course with no playground")
    from .webapp import _esc
    for _val, label in pack.topics:
        if _esc(label) not in html:
            errs.append(f"render: topic label {label!r} missing from "
                        "focus dropdown")
    for ch in sorted(pack.ch_weight):
        if f"{pack.unit_label} {ch}" not in html:
            errs.append(f"render: '{pack.unit_label} {ch}' missing from "
                        "focus dropdown")
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", suffix=".html",
                                         delete=False) as f:
            f.write(html)
            page = f.name
        with tempfile.NamedTemporaryFile("w", suffix=".js",
                                         delete=False) as f:
            f.write(NODE_SHIM)
            shim = f.name
        try:
            r = subprocess.run([node, shim, page], capture_output=True,
                               text=True, timeout=30)
            if r.returncode:
                errs.append("render: page JS crashed under node: "
                            + (r.stderr or "").strip()[:160])
        finally:
            os.unlink(page)
            os.unlink(shim)
    else:
        warns.append("node not installed \u2014 page JS not executed "
                     "(structural checks only)")

# ---------------------------------------------------------------------------
# main validators
# ---------------------------------------------------------------------------

def validate_pack(pack, out=None):
    p = out.append if out is not None else print
    errs, warns = [], []
    ok = lambda m: p("  \u2713 " + m)

    _framework(errs)

    # --- manifest + payload -------------------------------------------------
    for field in ("code", "name", "blurb", "badge"):
        lint_text(getattr(pack, field, ""), f"manifest {field}", errs)
    if pack.status not in ("active", "template"):
        errs.append(f"manifest: status {pack.status!r} invalid")
    folder = os.path.basename(pack.dir)
    if pack.slug != folder or pack.slug != pack.slug.lower():
        errs.append(f"manifest: slug {pack.slug!r} must equal (lowercase) "
                    f"folder name {folder!r}")
    tot = sum(pack.ch_weight.values())
    if abs(tot - 1.0) > 0.02:
        errs.append(f"blueprint: CH_WEIGHT sums to {tot:.2f}, expected 1.0")
    if any(w <= 0 for w in pack.ch_weight.values()):
        errs.append("blueprint: non-positive chapter weight")
    for ch in pack.ch_weight:
        if ch not in pack.chapter_names:
            warns.append(f"chapter {ch} has no name \u2014 dropdown shows "
                         "a blank suffix")
    inv_path = os.path.join(pack.dir, "inventory.json")
    valid_refs = None
    if os.path.exists(inv_path):
        try:
            def _collect(d, acc):
                for k, v in d.items():
                    if isinstance(v, dict):
                        if isinstance(v.get("sections"), dict):
                            acc.update(map(str, v["sections"].keys()))
                        else:
                            _collect(v, acc)
                    elif "." in str(k):
                        acc.add(str(k))
            valid_refs = set()
            _collect(json.load(open(inv_path)), valid_refs)
            if not valid_refs:
                errs.append("inventory.json parsed but contains no "
                            "section refs")
                valid_refs = None
        except Exception as e:
            errs.append(f"inventory.json unreadable: {e}")
            valid_refs = None
    else:
        warns.append("no inventory.json \u2014 concept \u00a7refs are "
                     "UNVERIFIED against the source; save the "
                     "course-study-guide coverage audit's inventory as "
                     "inventory.json in this pack")
    for cid, c in pack.concepts.items():
        if not all(k in c for k in ("ch", "ref", "name")):
            errs.append(f"concept {cid}: needs ch/ref/name")
            continue
        lint_text(c["name"], f"concept {cid} name", errs)
        if c["ch"] not in pack.ch_weight:
            errs.append(f"concept {cid}: chapter {c['ch']} not in CH_WEIGHT")
        ref = str(c["ref"])
        if not any(ch.isdigit() for ch in ref):
            warns.append(f"concept {cid}: ref {ref!r} has no number")
        m = re.match(r"(\d+)\.", ref)
        if m and int(m.group(1)) != c["ch"]:
            errs.append(f"concept {cid}: ref \u00a7{ref} lives in chapter "
                        f"{m.group(1)} but ch={c['ch']} \u2014 tag and "
                        "mastery map would lie")
        if valid_refs is not None and ref not in valid_refs:
            errs.append(f"concept {cid}: \u00a7{ref} is not in the "
                        "source inventory \u2014 phantom reference; "
                        "\"review \u00a7X\" advice would point nowhere")
    for val, label in pack.topics:
        if val != val.lower():
            errs.append(f"topic keyword {val!r} must be lowercase")
        if val.isdigit():
            errs.append(f"topic keyword {val!r} is numeric \u2014 collides "
                        "with chapter filtering")
        probe = [{"concept": cid} for cid in pack.concepts]
        if not any(_topic_match(q, val, pack.concepts) for q in probe):
            errs.append(f"topic {val!r} ({label}) matches no concept \u2014 "
                        "dead dropdown option")
    # pack import hygiene
    for fn in os.listdir(pack.dir):
        if not fn.endswith(".py"):
            continue
        src = open(os.path.join(pack.dir, fn)).read()
        for m in re.finditer(r"^\s*(?:from|import)\s+(core[.\w]*|courses[.\w]*)",
                             src, re.M):
            mod = m.group(1)
            if mod.startswith("courses") and pack.slug not in mod:
                errs.append(f"{fn}: imports another pack ({mod}) \u2014 "
                            "packs must be self-contained")
            if mod.startswith("core") and not mod.startswith(
                    "core.playgrounds"):
                errs.append(f"{fn}: imports {mod} \u2014 packs may import "
                            "only core.playgrounds")
    if not os.path.exists(os.path.join(pack.dir, "__init__.py")):
        errs.append("pack missing __init__.py")
    sg = os.path.join(pack.dir, "study_guide.pdf")
    if os.path.exists(sg):
        head = open(sg, "rb").read(8)
        if not head.startswith(b"%PDF") or os.path.getsize(sg) < 10240:
            errs.append("study_guide.pdf is not a real PDF (bad magic or "
                        "under 10KB)")
    else:
        warns.append("no study_guide.pdf yet \u2014 required before "
                     "delivery (course-study-guide skill)")
    if not errs:
        ok(f"manifest + payload ({len(pack.concepts)} concepts, "
           f"{len(pack.ch_weight)} chapters, {len(pack.topics)} topics)")

    # --- sample databases ---------------------------------------------------
    if pack.sample_dbs:
        from .engine import Engine
        with tempfile.TemporaryDirectory() as td:
            eng = Engine(td, pack.sample_dbs, pack.db_descriptions)
            for name in pack.sample_dbs:
                try:
                    eng.use(name)
                    for t in eng.tables(name):
                        eng.describe(t)
                except Exception as e:
                    errs.append(f"database {name}: {e}")
        ok(f"{len(pack.sample_dbs)} sample databases build + describe")

    # --- playground ---------------------------------------------------------
    from .playgrounds import blocks_text
    pg = pack.playground
    if pg == "__unstipulated__":
        errs.append("pack must stipulate PLAYGROUND = <backend> or None "
                    "(with PLAYGROUND_NOTE recording the user's decision)")
    elif pg is None:
        if not pack.playground_note:
            errs.append("PLAYGROUND = None requires a PLAYGROUND_NOTE")
        else:
            ok("playground stipulated: none \u2014 "
               + pack.playground_note[:60])
    else:
        with tempfile.TemporaryDirectory() as td:
            try:
                pg.bind(td)
                lint_text(getattr(pg, "label", ""), "playground label", errs)
                lint_text(getattr(pg, "placeholder", ""),
                          "playground placeholder", errs, mode="code")
                sc = pg.selfcheck()
                if len(sc) < 2:
                    errs.append(f"playground '{pg.kind}': selfcheck() must "
                                "return >=2 checks")
                for i, (src, stdin, want) in enumerate(sc):
                    r = pg.run(src, stdin)
                    if want not in blocks_text(r.get("blocks", [])):
                        errs.append(f"playground '{pg.kind}' selfcheck {i}: "
                                    f"{want!r} not in output")
                        break
                for junk in ("", "\u00a7\u00a7 garbage \u00a7\u00a7 ((("):
                    r = pg.run(junk)
                    if not isinstance(r, dict) or "blocks" not in r:
                        errs.append(f"playground '{pg.kind}': run() on "
                                    "junk returned malformed result")
                        break
                side = pg.sidebar()
                if side is not None and side.get("reset_all"):
                    if not pg.reset("all"):
                        errs.append(f"playground '{pg.kind}': reset "
                                    "returned no message")
                ok(f"playground '{pg.kind}' \u2014 {len(sc)} selfchecks + "
                   "junk-input resilience")
            except Exception as e:
                errs.append(f"playground '{pg.kind}': {e!r}")

    ctx = QuizContext(pack.sample_dbs)
    hit = set()
    hit_ch = set()

    # --- MCQ generators -----------------------------------------------------
    n_inst = 0
    pre_errs = len(errs)
    lint_bypass = set()
    for gen in pack.mcq_generators:
        gname = getattr(gen, "__name__", str(gen))
        variety = set()
        for s in range(MCQ_SEEDS):
            rng = random.Random(_seed(gname, 7, s))
            try:
                q = gen(rng, ctx)
            except Exception as e:
                errs.append(f"{gname} (seed {s}): raised {e!r}")
                break
            if _q_key(q) != _q_key(gen(random.Random(_seed(gname, 7, s)),
                                       ctx)):
                errs.append(f"{gname} (seed {s}): not deterministic for a "
                            "fixed seed \u2014 uses global random/state")
                break
            n_inst += 1
            if q.get("lint") == "code":
                lint_bypass.add(gname)
            check_question(q, gname, s, pack, errs, warns)
            if q.get("concept") in pack.concepts:
                hit.add(q["concept"])
                hit_ch.add(pack.concepts[q["concept"]]["ch"])
            variety.add((str(q.get("prompt")),
                         tuple(map(str, q.get("options", []))) if
                         isinstance(q.get("options"), list) else ()))
        if len(variety) == 1 and MCQ_SEEDS > 1:
            warns.append(f"{gname}: identical across {MCQ_SEEDS} seeds "
                         "\u2014 memorizable; consider varying")
    if lint_bypass:
        warns.append('lint="code" pattern-lint bypass used by: '
                     + ", ".join(sorted(lint_bypass))
                     + " \u2014 disposition each in the delivery message")
    if len(errs) == pre_errs:
        ok(f"{len(pack.mcq_generators)} MCQ generators \u2014 {n_inst} "
           "instances typed, linted, leak-checked, deterministic")

    # --- SQL generators -----------------------------------------------------
    n_sql = 0
    pre_errs = len(errs)
    for gen in pack.sql_generators:
        gname = getattr(gen, "__name__", str(gen))
        for s in range(SQL_SEEDS):
            rng = random.Random(_seed(gname, 11, s))
            try:
                t = gen(rng, ctx)
            except Exception as e:
                errs.append(f"{gname} (seed {s}): raised {e!r}")
                break
            if _q_key(t) != _q_key(gen(random.Random(_seed(gname, 11, s)),
                                       ctx)):
                errs.append(f"{gname} (seed {s}): not deterministic for a "
                            "fixed seed")
                break
            n_sql += 1
            if t.get("concept") not in pack.concepts:
                errs.append(f"{gname}: unknown concept {t.get('concept')!r}")
                break
            hit.add(t["concept"])
            hit_ch.add(pack.concepts[t["concept"]]["ch"])
            if t.get("db") not in pack.sample_dbs:
                errs.append(f"{gname} (seed {s}): db {t.get('db')!r} not in "
                            "SAMPLE_DBS")
                break
            lint_text(t.get("prompt"), f"{gname} (seed {s}) prompt", errs)
            if t.get("hint"):
                lint_text(t["hint"], f"{gname} (seed {s}) hint", errs,
                          mode="code")
            good, fb = check_sql_task(t, t["reference"], ctx)
            if not good:
                errs.append(f"{gname} (seed {s}): reference fails its own "
                            f"grader: {fb[:1]}")
                break
            if t.get("kind") == "select":
                try:
                    _h, r1 = ctx.q(t["db"], t["reference"])
                    _h, r2 = ctx.q(t["db"], t["reference"])
                    if not r1:
                        errs.append(f"{gname} (seed {s}): reference returns "
                                    "0 rows \u2014 unanswerable")
                        break
                    if r1 != r2:
                        errs.append(f"{gname} (seed {s}): reference "
                                    "non-deterministic (RAND()/now()?)")
                        break
                except Exception as e:
                    errs.append(f"{gname} (seed {s}): reference errored: {e}")
                    break
            junk_ok, _ = check_sql_task(t, "SELECT 1;", ctx)
            if junk_ok and t.get("kind") != "ddl":
                errs.append(f"{gname} (seed {s}): junk answer graded correct")
                break
    if pack.sql_generators and len(errs) == pre_errs:
        ok(f"{len(pack.sql_generators)} SQL tasks \u2014 {n_sql} instances "
           "graded, answerable, deterministic")

    # --- coverage -----------------------------------------------------------
    missed = set(pack.concepts) - hit
    if missed:
        errs.append(f"concepts never generated: {sorted(missed)}")
    ch_missed = set(pack.ch_weight) - hit_ch
    if ch_missed:
        errs.append(f"blueprint chapters with zero questions: "
                    f"{sorted(ch_missed)} \u2014 the blueprint demands "
                    "questions that cannot exist")
    if not missed and not ch_missed:
        ok(f"coverage: {len(hit)}/{len(pack.concepts)} concepts, "
           f"{len(hit_ch)}/{len(pack.ch_weight)} chapters")

    # --- selection-path integration ----------------------------------------
    pre_errs = len(errs)
    rng = random.Random(4242)
    got = pick_questions(8, {}, rng, ctx, pack.mcq_generators,
                         pack.concepts, pack.ch_weight)
    if len(got) < min(8, len(pack.mcq_generators)):
        errs.append(f"pick_questions returned {len(got)}/8 with empty stats")
    for val, label in pack.topics:
        if not any(_topic_match({"concept": cid}, val, pack.concepts)
                   for cid in hit):
            errs.append(f"topic {val!r} ({label}): no generated question "
                        "can ever match it \u2014 dead drill option")
    for ch in sorted(pack.ch_weight):
        if ch not in hit_ch:
            pass  # already reported as blueprint-chapter gap
    if len(errs) == pre_errs:
        ok("selection path: blueprint drill works; every topic reachable "
           "from generated questions")

    # --- cross-process determinism ------------------------------------------
    pre_errs = len(errs)
    _cross_process_fingerprint(pack, errs)
    if not _is_child() and len(errs) == pre_errs:
        ok("cross-process fingerprint identical (no hash()/set-order "
           "dependence)")

    # --- render -------------------------------------------------------------
    pre_errs = len(errs)
    _render_checks(pack, errs, warns)
    if len(errs) == pre_errs:
        ok("render: tabs match capabilities, tokens filled, dropdown "
           "complete" + (", page JS executes" if shutil.which("node")
                         else ""))

    p(f"  SQLite: {sqlite3.sqlite_version}")
    for w in warns:
        p("  \u26a0 " + w)
    if errs:
        p(f"  {len(errs)} PROBLEM(S):")
        for x in errs:
            p("   - " + x)
        return False
    p("  All checks passed.")
    return True

def validate_all(packs, out=None):
    p = out.append if out is not None else print
    good = True
    for pk in packs:
        p(f"[{pk.code}] {pk.name}")
        good = validate_pack(pk, out) and good
    return good


# ---------------------------------------------------------------------------
# selfproof: a synthetic bad pack the harness MUST fail loudly.
# Run after any harness edit:  python3 -m core.harness
# ---------------------------------------------------------------------------

def _bad_pack(tmpdir):
    import types
    d = os.path.join(tmpdir, "zbad")
    os.makedirs(d)
    open(os.path.join(d, "__init__.py"), "w").write("")
    concepts = {"a": {"ch": 1, "ref": "1.1", "name": "Alpha"},
                "b": {"ch": 2, "ref": "2.1", "name": "Beta"},
                "c": {"ch": 1, "ref": "2.9", "name": "Mismatch"}}
    open(os.path.join(d, "inventory.json"), "w").write(
        '{"1": {"sections": {"1.1": "One"}},'
        ' "2": {"sections": {"2.1": "Two"}}}')

    def g_screenshot_bug(rng, ctx):        # the July 2026 flowchart bug
        pair = rng.choice([("an input or output statement",
                            "Parallelogram")])
        return {"concept": "a", "type": "mcq",
                "prompt": f"In a flowchart, which shape represents {pair}?",
                "options": [["Parallelogram", "Oval", "Rectangle"],
                            "Diamond", "Oval", "Rectangle"],
                "answer": 0, "explain": f"{pair} explained at length here."}

    def g_leftovers(rng, ctx):
        return {"concept": "a", "type": "mcq",
                "prompt": "What is {n} plus %s for token %%CODE%%, TODO?",
                "options": ["one", "two", "two", "all of the above",
                            "x", "y"],
                "answer": 0, "explain": "short"}

    def g_giveaway(rng, ctx):
        return {"concept": "a", "type": "mcq",
                "prompt": "The HAVING clause filters groups. Which clause "
                          "filters groups?",
                "options": ["HAVING clause", "WHERE", "ORDER BY"],
                "answer": 0,
                "explain": "HAVING filters groups after aggregation."}

    def g_bypass(rng, ctx):
        return {"concept": "a", "type": "mcq", "lint": "code",
                "prompt": "Raw code shown: for (i = 0; i < n; i++) { }",
                "options": ["loop", "branch", "cast"], "answer": 0,
                "explain": "The bypass itself must surface as a warning."}

    def g_impure(rng, ctx):                 # ignores rng entirely
        import random as _r
        v = _r.randint(1, 10 ** 6)
        return {"concept": "a", "type": "mcq",
                "prompt": f"Impure value {v} means what exactly here?",
                "options": [str(v), str(v + 1), str(v + 2)], "answer": 0,
                "explain": "This generator is not a function of rng."}

    return types.SimpleNamespace(
        slug="zbad", code="Z000", name="Bad Pack", blurb="x", badge="x",
        status="bogus", dir=d, unit_label="Chapter",
        chapter_names={1: "One"}, topics=[("nomatch", "Dead Topic"),
                                          ("7", "Numeric")],
        concepts=concepts, ch_weight={1: 0.5, 2: 0.5},
        mcq_generators=[g_screenshot_bug, g_leftovers, g_giveaway,
                        g_bypass, g_impure],
        sql_generators=[], sample_dbs={}, db_descriptions={},
        playground="__unstipulated__", playground_note="",
        has_playground=False, study_guide_path=None)

def selfproof():
    must_catch = [
        "not a string",                 # list leaked as an option
        "tuple/list repr leaked",       # tuple f-stringed into prompt
        "unformatted {placeholder}",
        "printf-style leftover",
        "unreplaced template token",
        "dev placeholder marker",
        "duplicate options",
        "shuffle-hostile option",
        "UI keys support A",            # >5 breaks A-E keys
        "answer",                       # giveaway check
        "explain too short",
        "not deterministic",            # in-process purity
        "dead drill option",
        "numeric",                      # numeric topic keyword
        "status",
        "must stipulate PLAYGROUND",
        "never generated",              # concept b unreachable
        "zero questions",               # chapter 2 unreachable
        "phantom reference",            # ref not in inventory.json
        "but ch=",                      # ref chapter != concept ch
        'lint="code" pattern-lint bypass used by: g_bypass',
    ]
    os.environ["WGU_HARNESS_CHILD"] = "1"   # skip subprocess for synthetic
    out = []
    with tempfile.TemporaryDirectory() as td:
        okp = validate_pack(_bad_pack(td), out)
    text = "\n".join(out)
    missing = [m for m in must_catch if m not in text]
    if okp or missing:
        print(text)
        print("SELFPROOF FAILED \u2014 harness lost its teeth. "
              f"pass={okp} missing={missing}")
        return False
    print(f"selfproof: harness caught all {len(must_catch)} planted "
          "defect classes in the synthetic bad pack.")
    return True

if __name__ == "__main__":
    sys.exit(0 if selfproof() else 1)
