"""Terminal colors + result-table rendering (shared by engine + CLI)."""
import os
import sys
import textwrap

# ---------------------------------------------------------------------------
# Terminal colors
# ---------------------------------------------------------------------------

def _supports_color():
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None and os.environ.get("TERM") != "dumb"

USE_COLOR = _supports_color()

def _c(code, s):
    return f"\033[{code}m{s}\033[0m" if USE_COLOR else str(s)

def bold(s):    return _c("1", s)
def dim(s):     return _c("2", s)
def red(s):     return _c("31", s)
def green(s):   return _c("32", s)
def yellow(s):  return _c("33", s)
def blue(s):    return _c("34", s)
def magenta(s): return _c("35", s)
def cyan(s):    return _c("36", s)

def wrap(s, width=78, indent=""):
    out = []
    for para in s.split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width, initial_indent=indent,
                                 subsequent_indent=indent))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Result printing (MySQL client look)
# ---------------------------------------------------------------------------

def _fmt_val(v):
    if v is None:
        return "NULL"
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return f"{v:.2f}" if abs(v) >= 1000 else f"{v:g}"
        return f"{round(v, 6):g}"
    return str(v)

def print_result(headers, rows, elapsed=None, max_rows=200, out=None):
    p = (out.append if out is not None else print)
    if not headers:
        p(dim("(no result)"))
        return
    shown = rows[:max_rows]
    cells = [[_fmt_val(v) for v in r] for r in shown]
    widths = [len(h) for h in headers]
    for r in cells:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(v))
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    p(sep)
    p("| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |")
    p(sep)
    for r in cells:
        p("| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(r)) + " |")
    p(sep)
    n = len(rows)
    extra = f" (showing first {max_rows})" if n > max_rows else ""
    t = f" ({elapsed:.3f} sec)" if elapsed is not None else ""
    p(dim(f"{n} row{'s' if n != 1 else ''} in set{extra}{t}"))

