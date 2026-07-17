"""Playground port — the language-agnostic contract between course packs
and the hub's console UI. Core owns the UI and HTTP plumbing; a backend
owns what "run" means. Backends return DATA ONLY (blocks), never HTML.

Every pack MUST stipulate exactly one of:
    PLAYGROUND = SomeBackend(...)      # this course has a hands-on console
    PLAYGROUND = None                  # plus PLAYGROUND_NOTE = "why not"
The harness fails packs that are silent, and executes every backend's
selfcheck() before it can ship.

Backend contract (duck-typed; subclass PlaygroundBase for defaults):
    kind: str            short id ("sql", "python", "coral")
    label: str           console heading ("SQL console")
    placeholder: str     initial editor placeholder text
    stdin_enabled: bool  show a program-input box under the editor
    bind(data_dir)       lifecycle: called with the course's data dir
                         before any run/sidebar/reset; must be re-bindable
    run(source, stdin="") -> {"ok": bool, "blocks": [block, ...],
                              "notes": [str], "state": {...}}
    sidebar() -> None | {"title", "sub", "reset_all": str|None,
                         "groups": [{"name", "desc", "on": bool,
                                     "reset": bool,
                                     "items": [{"label", "run",
                                                "title"?, "alt_run"?,
                                                "alt_title"?}]}]}
    selector() -> None | {"label", "options": [str], "current": str,
                          "run_template": "USE {value};"}
    reset(target=None) -> str message   (only if sidebar offers reset)
    selfcheck() -> [(source, stdin, expected_substring), ...]  (>=2)

block shapes (rendered by core's JS):
    {"kind": "table", "headers", "rows", "total", "truncated",
     "notes"?: [str]}
    {"kind": "ok"|"text"|"error", "text": str, "notes"?: [str]}

Boundaries every backend honors:
- Never execute without a wall-clock timeout (subprocess) or step budget
  (in-process interpreter). Cap output size. No network. Scratch files
  only under the bound data_dir.
- Language semantics come from the course's own materials, never memory.
- Single-course backends live in the pack (courses/<slug>/); backends
  shared by several courses live here in core/playgrounds/ — adding one
  is a deliberate, user-approved core change.
"""

def jval(v):
    if v is None or isinstance(v, (int, float, str)):
        return v
    return str(v)

def rows_json(rows, cap=500):
    out = [[jval(v) for v in r] for r in rows[:cap]]
    return out, len(rows), len(rows) > cap

def blocks_text(blocks):
    """Serialize blocks for selfcheck substring matching."""
    parts = []
    for b in blocks:
        if b.get("kind") == "table":
            parts.append(" | ".join(str(h) for h in b["headers"]))
            for r in b["rows"]:
                parts.append(" | ".join("NULL" if v is None else str(v)
                                        for v in r))
        else:
            parts.append(str(b.get("text", "")))
        parts.extend(b.get("notes") or [])
    return "\n".join(parts)

class PlaygroundBase:
    kind = "generic"
    label = "Playground"
    placeholder = ""
    stdin_enabled = False

    def bind(self, data_dir):
        self.data_dir = data_dir

    def run(self, source, stdin=""):
        raise NotImplementedError

    def sidebar(self):
        return None

    def selector(self):
        return None

    def reset(self, target=None):
        raise NotImplementedError("this backend has no reset")

    def selfcheck(self):
        return []
