"""Coral interpreter for the D278 playground.

Coral is the pedagogical language D278 actually teaches (the course title says
"Scripting and Programming" and the OA is C++-flavored in name only). This is a
real tokenize -> parse -> evaluate interpreter; there is no regex transpile.

EVERY semantic rule below is traceable to a section of the uploaded zyBooks
chapters, and the section ref is cited next to the rule. Where the chapters are
silent, the choice is marked SILENT: and matches the zyBooks simulator behavior
the chapters describe.

Source-verified semantics
-------------------------
§1.3   A comment starts with // and runs to end of line. The chapters state the
       comment "must be on its own line"; we accept trailing comments too and
       note it (accepting a superset never breaks a valid course program).
§2.1   `x = Get next input` reads ONE whitespace-separated token.
§2.2   `Put <expr> to output` writes with NO separator and NO newline.
       `Put newline to output` is how a newline is emitted -- `newline` is a
       KEYWORD, not the string "\\n". (Verified: ch2 measles example.)
§2.10  "When the operands of / are both integers, the operator performs integer
       division, which does not generate any fraction. The / operator performs
       floating-point division if at least one operand is a floating-point
       type." Truncation is toward zero.
§2.12  "% evaluates to the remainder of the division of two integer operands."
§2.13  Types: integer, float, boolean, string, character.
§2.14  Constants: `constant integer NAME = value` -- reassignment is an error.
§3.1-2 if / elseif / else, blocks by INDENTATION.
§3.3   == != < <= > >=          §3.5  and / or / not
§4.x   while; do..while; for i = 0; i < N; i = i + 1
§5.1   `integer array(N) name`, 0-based `name[i]`, `name.size`.
§6.1-2 `Function F(integer p) returns integer r` -- the body assigns the NAMED
       RETURN VARIABLE r, which is what the call evaluates to. An explicit
       `return <expr>` also appears (ch7 search algorithms) and is supported.
       `Function Main() returns nothing` is an accepted entry point; bare
       top-level statements also run, as the chapters' snippets do.

Isolation: the interpreter runs IN-PROCESS, so there is no wall-clock timeout to
lean on. Instead every evaluation step is counted against a STEP BUDGET; an
infinite loop exhausts it and returns an error block rather than hanging the
hub. Output is capped too.
"""

STEP_BUDGET = 500_000
OUTPUT_CAP = 20_000

TYPES = ("integer", "float", "boolean", "string", "character")
KEYWORDS = {
    "if", "elseif", "else", "while", "for", "do", "Put", "to", "output",
    "Get", "next", "input", "Function", "returns", "return", "nothing",
    "and", "or", "not", "true", "false", "array", "newline", "constant",
} | set(TYPES)


class CoralError(Exception):
    """A user-facing program error (syntax or runtime)."""
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(msg)

    def __str__(self):
        return (f"Line {self.line}: {self.msg}" if self.line else self.msg)


class StepBudgetExceeded(CoralError):
    pass


# =====================================================================
# 1. TOKENIZER  — indentation is significant (blocks are indented, §3.1)
# =====================================================================
class Tok:
    __slots__ = ("kind", "val", "line")

    def __init__(self, kind, val, line):
        self.kind, self.val, self.line = kind, val, line

    def __repr__(self):
        return f"{self.kind}:{self.val!r}"


OPS = ["==", "!=", "<=", ">=", "<", ">", "+", "-", "*", "/", "%", "=",
       "(", ")", "[", "]", ";", ",", "."]


def tokenize(src):
    toks = []
    indents = [0]
    lines = src.replace("\t", "    ").split("\n")

    for ln, raw in enumerate(lines, start=1):
        # §1.3 — // comment runs to end of line
        code = raw.split("//", 1)[0]
        if not code.strip():
            continue                      # blank / comment-only line: no tokens

        indent = len(code) - len(code.lstrip(" "))
        body = code.strip()

        if indent > indents[-1]:
            indents.append(indent)
            toks.append(Tok("INDENT", indent, ln))
        else:
            while indent < indents[-1]:
                indents.pop()
                toks.append(Tok("DEDENT", indent, ln))
            if indent != indents[-1]:
                raise CoralError("inconsistent indentation", ln)

        i = 0
        while i < len(body):
            c = body[i]
            if c == " ":
                i += 1
                continue
            if c == '"':                                  # string literal
                j = i + 1
                buf = []
                while j < len(body) and body[j] != '"':
                    if body[j] == "\\" and j + 1 < len(body):
                        nxt = body[j + 1]
                        buf.append({"n": "\n", "t": "\t", '"': '"',
                                    "\\": "\\"}.get(nxt, nxt))
                        j += 2
                        continue
                    buf.append(body[j])
                    j += 1
                if j >= len(body):
                    raise CoralError("unterminated string literal", ln)
                toks.append(Tok("STR", "".join(buf), ln))
                i = j + 1
                continue
            if c.isdigit():                               # number
                j = i
                seen_dot = False
                while j < len(body) and (body[j].isdigit() or
                                         (body[j] == "." and not seen_dot and
                                          j + 1 < len(body) and
                                          body[j + 1].isdigit())):
                    if body[j] == ".":
                        seen_dot = True
                    j += 1
                text = body[i:j]
                toks.append(Tok("NUM", float(text) if seen_dot else int(text), ln))
                i = j
                continue
            if c.isalpha() or c == "_":                   # identifier / keyword
                j = i
                while j < len(body) and (body[j].isalnum() or body[j] == "_"):
                    j += 1
                word = body[i:j]
                toks.append(Tok("KW" if word in KEYWORDS else "ID", word, ln))
                i = j
                continue
            for op in OPS:                                # operator
                if body.startswith(op, i):
                    toks.append(Tok("OP", op, ln))
                    i += len(op)
                    break
            else:
                raise CoralError(f"unexpected character {c!r}", ln)

        toks.append(Tok("NEWLINE", None, ln))

    while len(indents) > 1:
        indents.pop()
        toks.append(Tok("DEDENT", 0, len(lines)))
    toks.append(Tok("EOF", None, len(lines)))
    return toks


# =====================================================================
# 2. PARSER — recursive descent -> AST (tuples: (op, ...))
# =====================================================================
class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    # -- token helpers ------------------------------------------------
    def peek(self, k=0):
        return self.t[min(self.i + k, len(self.t) - 1)]

    def at(self, kind, val=None):
        tk = self.peek()
        return tk.kind == kind and (val is None or tk.val == val)

    def eat(self, kind=None, val=None):
        tk = self.peek()
        if kind and (tk.kind != kind or (val is not None and tk.val != val)):
            got = tk.val if tk.val is not None else tk.kind
            want = val or kind
            raise CoralError(f"expected {want!r} but found {got!r}", tk.line)
        self.i += 1
        return tk

    def skip_newlines(self):
        while self.at("NEWLINE"):
            self.i += 1

    # -- entry --------------------------------------------------------
    def parse_program(self):
        stmts, funcs = [], {}
        self.skip_newlines()
        while not self.at("EOF"):
            if self.at("KW", "Function"):
                f = self.parse_function()
                funcs[f[1]] = f
            else:
                stmts.append(self.parse_statement())
            self.skip_newlines()
        return stmts, funcs

    def parse_block(self):
        """An indented block of statements (§3.1 — blocks are by indentation)."""
        self.skip_newlines()
        if not self.at("INDENT"):
            tk = self.peek()
            raise CoralError("expected an indented block here", tk.line)
        self.eat("INDENT")
        stmts = []
        self.skip_newlines()
        while not self.at("DEDENT") and not self.at("EOF"):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        if self.at("DEDENT"):
            self.eat("DEDENT")
        return stmts

    # -- functions (§6.1) ---------------------------------------------
    def parse_function(self):
        line = self.peek().line
        self.eat("KW", "Function")
        name = self.eat("ID").val
        self.eat("OP", "(")
        params = []
        while not self.at("OP", ")"):
            ptype = self.eat("KW").val               # integer / float / ...
            if ptype not in TYPES:
                raise CoralError(f"{ptype!r} is not a type", line)
            is_arr = False
            if self.at("KW", "array"):               # integer array[] name
                self.eat("KW", "array")
                if self.at("OP", "["):
                    self.eat("OP", "[")
                    self.eat("OP", "]")
                elif self.at("OP", "("):
                    self.eat("OP", "(")
                    while not self.at("OP", ")"):
                        self.eat()
                    self.eat("OP", ")")
                is_arr = True
            pname = self.eat("ID").val
            params.append((ptype, pname, is_arr))
            if self.at("OP", ","):
                self.eat("OP", ",")
        self.eat("OP", ")")
        self.eat("KW", "returns")
        # `returns nothing` (a procedure) or `returns <type> <retvar>` (§6.2)
        if self.at("KW", "nothing"):
            self.eat("KW", "nothing")
            rtype, rname = None, None
        else:
            rtype = self.eat("KW").val
            if rtype not in TYPES:
                raise CoralError(f"{rtype!r} is not a type", line)
            if self.at("KW", "array"):
                self.eat("KW", "array")
                if self.at("OP", "["):
                    self.eat("OP", "[")
                    self.eat("OP", "]")
            rname = self.eat("ID").val
        self.eat("NEWLINE")
        body = self.parse_block()
        return ("func", name, params, rtype, rname, body, line)

    # -- statements ---------------------------------------------------
    def parse_statement(self):
        tk = self.peek()
        line = tk.line

        if tk.kind == "KW":
            if tk.val == "constant":                        # §2.14
                self.eat("KW", "constant")
                vtype = self.eat("KW").val
                name = self.eat("ID").val
                self.eat("OP", "=")
                expr = self.parse_expr()
                self.eat("NEWLINE")
                return ("const", vtype, name, expr, line)

            if tk.val in TYPES:                             # declaration
                vtype = self.eat("KW").val
                if self.at("KW", "array"):                  # §5.1
                    self.eat("KW", "array")
                    self.eat("OP", "(")
                    size = self.parse_expr()
                    self.eat("OP", ")")
                    name = self.eat("ID").val
                    self.eat("NEWLINE")
                    return ("declare_arr", vtype, name, size, line)
                name = self.eat("ID").val
                init = None
                if self.at("OP", "="):
                    self.eat("OP", "=")
                    init = self.parse_rhs()
                self.eat("NEWLINE")
                return ("declare", vtype, name, init, line)

            if tk.val == "Put":                             # §2.2
                self.eat("KW", "Put")
                if self.at("KW", "newline"):
                    self.eat("KW", "newline")
                    node = ("newline",)
                else:
                    node = self.parse_expr()
                self.eat("KW", "to")
                self.eat("KW", "output")
                self.eat("NEWLINE")
                return ("put", node, line)

            if tk.val == "if":
                return self.parse_if()
            if tk.val == "while":
                self.eat("KW", "while")
                cond = self.parse_expr()
                self.eat("NEWLINE")
                body = self.parse_block()
                return ("while", cond, body, line)
            if tk.val == "do":                              # §4.9
                self.eat("KW", "do")
                self.eat("NEWLINE")
                body = self.parse_block()
                self.eat("KW", "while")
                cond = self.parse_expr()
                self.eat("NEWLINE")
                return ("dowhile", cond, body, line)
            if tk.val == "for":                             # §4.4
                self.eat("KW", "for")
                init = self.parse_simple()
                self.eat("OP", ";")
                cond = self.parse_expr()
                self.eat("OP", ";")
                update = self.parse_simple()
                self.eat("NEWLINE")
                body = self.parse_block()
                return ("for", init, cond, update, body, line)
            if tk.val == "return":                          # §7 (search algos)
                self.eat("KW", "return")
                expr = None
                if not self.at("NEWLINE"):
                    expr = self.parse_expr()
                self.eat("NEWLINE")
                return ("return", expr, line)
            if tk.val == "Function":
                raise CoralError("a function cannot be defined inside a block",
                                 line)

        # assignment, indexed assignment, or a bare call
        st = self.parse_simple()
        self.eat("NEWLINE")
        return st

    def parse_simple(self):
        """Assignment / indexed assignment / bare call (no NEWLINE consumed)."""
        tk = self.peek()
        line = tk.line
        if tk.kind == "ID":
            if self.peek(1).kind == "OP" and self.peek(1).val == "=":
                name = self.eat("ID").val
                self.eat("OP", "=")
                return ("assign", name, self.parse_rhs(), line)
            if self.peek(1).kind == "OP" and self.peek(1).val == "[":
                name = self.eat("ID").val
                self.eat("OP", "[")
                idx = self.parse_expr()
                self.eat("OP", "]")
                if self.at("OP", "="):
                    self.eat("OP", "=")
                    return ("assign_idx", name, idx, self.parse_rhs(), line)
                raise CoralError("expected '=' after an array element", line)
        expr = self.parse_expr()
        return ("exprstmt", expr, line)

    def parse_rhs(self):
        """Right side of '=' — either `Get next input` (§2.1) or an expression."""
        if self.at("KW", "Get"):
            line = self.peek().line
            self.eat("KW", "Get")
            self.eat("KW", "next")
            self.eat("KW", "input")
            return ("input", line)
        return self.parse_expr()

    def parse_if(self):
        line = self.peek().line
        self.eat("KW", "if")
        cond = self.parse_expr()
        self.eat("NEWLINE")
        body = self.parse_block()
        arms = [(cond, body)]
        els = []
        self.skip_newlines()
        while self.at("KW", "elseif"):                      # §3.2
            self.eat("KW", "elseif")
            c = self.parse_expr()
            self.eat("NEWLINE")
            arms.append((c, self.parse_block()))
            self.skip_newlines()
        if self.at("KW", "else"):
            self.eat("KW", "else")
            self.eat("NEWLINE")
            els = self.parse_block()
        return ("if", arms, els, line)

    # -- expressions (precedence per §3.6) ----------------------------
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.at("KW", "or"):
            line = self.eat("KW").line
            node = ("or", node, self.parse_and(), line)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.at("KW", "and"):
            line = self.eat("KW").line
            node = ("and", node, self.parse_not(), line)
        return node

    def parse_not(self):
        if self.at("KW", "not"):
            line = self.eat("KW").line
            return ("not", self.parse_not(), line)
        return self.parse_cmp()

    def parse_cmp(self):
        node = self.parse_add()
        while self.peek().kind == "OP" and self.peek().val in (
                "==", "!=", "<", "<=", ">", ">="):
            op = self.eat("OP")
            node = ("cmp", op.val, node, self.parse_add(), op.line)
        return node

    def parse_add(self):
        node = self.parse_mul()
        while self.peek().kind == "OP" and self.peek().val in ("+", "-"):
            op = self.eat("OP")
            node = ("bin", op.val, node, self.parse_mul(), op.line)
        return node

    def parse_mul(self):
        node = self.parse_unary()
        while self.peek().kind == "OP" and self.peek().val in ("*", "/", "%"):
            op = self.eat("OP")
            node = ("bin", op.val, node, self.parse_unary(), op.line)
        return node

    def parse_unary(self):
        if self.at("OP", "-"):
            line = self.eat("OP").line
            return ("neg", self.parse_unary(), line)
        return self.parse_primary()

    def parse_primary(self):
        tk = self.peek()
        line = tk.line
        if tk.kind == "NUM":
            self.eat("NUM")
            return ("num", tk.val, line)
        if tk.kind == "STR":
            self.eat("STR")
            return ("str", tk.val, line)
        if tk.kind == "KW" and tk.val in ("true", "false"):
            self.eat("KW")
            return ("bool", tk.val == "true", line)
        if tk.kind == "OP" and tk.val == "(":
            self.eat("OP", "(")
            node = self.parse_expr()
            self.eat("OP", ")")
            return node
        if tk.kind == "ID":
            name = self.eat("ID").val
            if self.at("OP", "("):                          # call
                self.eat("OP", "(")
                args = []
                while not self.at("OP", ")"):
                    args.append(self.parse_expr())
                    if self.at("OP", ","):
                        self.eat("OP", ",")
                self.eat("OP", ")")
                return ("call", name, args, line)
            if self.at("OP", "["):                          # index (§5.1)
                self.eat("OP", "[")
                idx = self.parse_expr()
                self.eat("OP", "]")
                return ("index", name, idx, line)
            if self.at("OP", "."):                          # .size (§5.1)
                self.eat("OP", ".")
                attr = self.eat().val
                if attr != "size":
                    raise CoralError(f"unknown attribute {attr!r}", line)
                return ("size", name, line)
            return ("var", name, line)
        raise CoralError(f"unexpected {tk.val if tk.val is not None else tk.kind!r}"
                         " in expression", line)


# =====================================================================
# 3. EVALUATOR — tree-walking, step-budgeted (no wall clock in-process)
# =====================================================================
import math


class _Return(Exception):
    def __init__(self, value):
        self.value = value


class Env:
    """One scope: values plus each variable's DECLARED type. The declared type
    matters — see coerce() and §2.10's own worked table."""
    def __init__(self, parent=None):
        self.vals = {}
        self.types = {}
        self.consts = set()
        self.parent = parent

    def declare(self, name, vtype, value, const=False):
        self.vals[name] = value
        self.types[name] = vtype
        if const:
            self.consts.add(name)

    def has(self, name):
        return name in self.vals or (self.parent and self.parent.has(name))

    def get(self, name, line):
        if name in self.vals:
            return self.vals[name]
        if self.parent:
            return self.parent.get(name, line)
        raise CoralError(f"variable {name!r} was never declared", line)

    def type_of(self, name):
        if name in self.types:
            return self.types[name]
        return self.parent.type_of(name) if self.parent else None

    def set(self, name, value, line):
        if name in self.vals:
            if name in self.consts:                       # §2.14
                raise CoralError(f"{name!r} is a constant and cannot be "
                                 "reassigned", line)
            self.vals[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value, line)
            return
        raise CoralError(f"variable {name!r} was never declared", line)


def coerce(vtype, value, line):
    """Store `value` into a variable declared `vtype`.

    §2.10's table shows why this matters: `f = c * (9 / 5) + 32` is "always
    c*1 + 32" because 9/5 is INTEGER division long before the float variable
    ever sees the result. Declared type does not retroactively fix arithmetic.
    """
    if vtype == "integer":
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, float):
            return math.trunc(value)                      # toward zero
        if isinstance(value, int):
            return value
        raise CoralError(f"cannot store {_typename(value)} in an integer", line)
    if vtype == "float":
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        raise CoralError(f"cannot store {_typename(value)} in a float", line)
    if vtype == "boolean":
        if isinstance(value, bool):
            return value
        raise CoralError(f"cannot store {_typename(value)} in a boolean", line)
    if vtype in ("string", "character"):
        return value if isinstance(value, str) else fmt(value)
    return value


def _typename(v):
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    return type(v).__name__


def fmt(v):
    """How a value appears via Put (§2.2).
    SILENT: the chapters don't specify float precision; zyBooks prints the
    shortest round-trip form, which is what Python's str() does."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e16:
            return f"{int(v)}.0"
        return repr(v)
    return str(v)


class Interp:
    def __init__(self, stdin_tokens, step_budget=STEP_BUDGET,
                 output_cap=OUTPUT_CAP):
        self.out = []
        self.out_len = 0
        self.truncated = False
        self.inputs = list(stdin_tokens)
        self.in_i = 0
        self.steps = 0
        self.budget = step_budget
        self.cap = output_cap
        self.funcs = {}

    # -- budget / output ----------------------------------------------
    def tick(self, line=None):
        self.steps += 1
        if self.steps > self.budget:
            raise StepBudgetExceeded(
                f"step budget of {self.budget:,} exceeded — this looks like an "
                "infinite loop (does the loop body change the loop variable?)",
                line)

    def emit(self, text):
        if self.truncated:
            return
        if self.out_len + len(text) > self.cap:
            self.out.append(text[: self.cap - self.out_len])
            self.truncated = True
            return
        self.out.append(text)
        self.out_len += len(text)

    def output(self):
        return "".join(self.out)

    # -- run ------------------------------------------------------------
    def run(self, stmts, funcs):
        self.funcs = funcs
        env = Env()
        # `Function Main() returns nothing` is an accepted entry point (§6.1);
        # bare top-level statements also run, as the chapters' snippets do.
        if not stmts and "Main" in funcs:
            self.call("Main", [], funcs["Main"][6], env)
            return
        self.exec_block(stmts, env)
        if not stmts and not funcs:
            return

    def exec_block(self, stmts, env):
        for st in stmts:
            self.exec(st, env)

    # -- statements -----------------------------------------------------
    def exec(self, st, env):
        op = st[0]
        self.tick(st[-1] if isinstance(st[-1], int) else None)

        if op == "declare":
            _, vtype, name, init, line = st
            val = self.eval(init, env) if init is not None else _zero(vtype)
            env.declare(name, vtype, coerce(vtype, val, line))

        elif op == "const":                                # §2.14
            _, vtype, name, expr, line = st
            env.declare(name, vtype,
                        coerce(vtype, self.eval(expr, env), line), const=True)

        elif op == "declare_arr":                          # §5.1
            _, vtype, name, size_e, line = st
            n = self.eval(size_e, env)
            if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                raise CoralError("array size must be a non-negative integer",
                                 line)
            env.declare(name, vtype + "[]", [_zero(vtype)] * n)

        elif op == "assign":
            _, name, rhs, line = st
            vtype = env.type_of(name)
            if vtype is None:
                raise CoralError(f"variable {name!r} was never declared", line)
            val = self.eval(rhs, env, want=vtype)
            env.set(name, coerce(vtype, val, line), line)

        elif op == "assign_idx":
            _, name, idx_e, rhs, line = st
            arr = env.get(name, line)
            if not isinstance(arr, list):
                raise CoralError(f"{name!r} is not an array", line)
            i = self.eval(idx_e, env)
            self.check_index(name, arr, i, line)
            base = (env.type_of(name) or "integer[]").replace("[]", "")
            arr[i] = coerce(base, self.eval(rhs, env, want=base), line)

        elif op == "put":                                  # §2.2
            _, node, line = st
            if node[0] == "newline":
                self.emit("\n")                            # `Put newline ...`
            else:
                self.emit(fmt(self.eval(node, env)))

        elif op == "if":
            _, arms, els, line = st
            for cond, body in arms:
                if truthy(self.eval(cond, env), line):
                    self.exec_block(body, env)
                    return
            self.exec_block(els, env)

        elif op == "while":
            _, cond, body, line = st
            while truthy(self.eval(cond, env), line):
                self.tick(line)
                self.exec_block(body, env)

        elif op == "dowhile":                              # §4.9 — body first
            _, cond, body, line = st
            while True:
                self.tick(line)
                self.exec_block(body, env)
                if not truthy(self.eval(cond, env), line):
                    break

        elif op == "for":                                  # §4.4
            _, init, cond, update, body, line = st
            self.exec(init, env)
            while truthy(self.eval(cond, env), line):
                self.tick(line)
                self.exec_block(body, env)
                self.exec(update, env)

        elif op == "return":
            _, expr, line = st
            raise _Return(self.eval(expr, env) if expr is not None else None)

        elif op == "exprstmt":
            self.eval(st[1], env)

        else:
            raise CoralError(f"cannot execute {op!r}", st[-1])

    def check_index(self, name, arr, i, line):
        if not isinstance(i, int) or isinstance(i, bool):
            raise CoralError("an array index must be an integer", line)
        if i < 0 or i >= len(arr):
            raise CoralError(
                f"index {i} is out of range for {name!r} — valid indices are "
                f"0 to {len(arr) - 1} (arrays are 0-based, §5.1)", line)

    # -- expressions ------------------------------------------------------
    def eval(self, e, env, want=None):
        self.tick(e[-1] if isinstance(e[-1], int) else None)
        op = e[0]

        if op == "num":
            return e[1]
        if op == "str":
            return e[1]
        if op == "bool":
            return e[1]
        if op == "var":
            return env.get(e[1], e[2])
        if op == "input":                                  # §2.1
            return self.read_input(want, e[1])
        if op == "index":
            _, name, idx_e, line = e
            arr = env.get(name, line)
            if not isinstance(arr, list):
                raise CoralError(f"{name!r} is not an array", line)
            i = self.eval(idx_e, env)
            self.check_index(name, arr, i, line)
            return arr[i]
        if op == "size":
            _, name, line = e
            arr = env.get(name, line)
            if not isinstance(arr, list):
                raise CoralError(f"{name!r} is not an array", line)
            return len(arr)
        if op == "neg":
            v = self.eval(e[1], env)
            _need_num(v, e[2])
            return -v
        if op == "not":
            return not truthy(self.eval(e[1], env), e[2])
        if op == "and":
            return (truthy(self.eval(e[1], env), e[3]) and
                    truthy(self.eval(e[2], env), e[3]))
        if op == "or":
            return (truthy(self.eval(e[1], env), e[3]) or
                    truthy(self.eval(e[2], env), e[3]))
        if op == "cmp":
            _, o, a, b, line = e
            x, y = self.eval(a, env), self.eval(b, env)
            if o == "==":
                return x == y
            if o == "!=":
                return x != y
            _need_num(x, line)
            _need_num(y, line)
            return {"<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y}[o]
        if op == "bin":
            return self.binop(e, env)
        if op == "call":
            _, name, args, line = e
            if name not in self.funcs:
                raise CoralError(f"no function named {name!r}", line)
            vals = [self.eval(a, env) for a in args]
            return self.call(name, vals, self.funcs[name][5], env, line)
        raise CoralError(f"cannot evaluate {op!r}", e[-1])

    def binop(self, e, env):
        _, o, a, b, line = e
        x = self.eval(a, env)
        y = self.eval(b, env)

        if o == "+" and (isinstance(x, str) or isinstance(y, str)):
            return fmt(x) + fmt(y)

        _need_num(x, line)
        _need_num(y, line)
        both_int = (isinstance(x, int) and not isinstance(x, bool) and
                    isinstance(y, int) and not isinstance(y, bool))

        if o == "+":
            return x + y
        if o == "-":
            return x - y
        if o == "*":
            return x * y
        if o == "/":
            # §2.10 — VERBATIM: "When the operands of / are both integers, the
            # operator performs integer division, which does not generate any
            # fraction. The / operator performs floating-point division if at
            # least one operand is a floating-point type."
            if y == 0:
                raise CoralError("division by zero", line)
            if both_int:
                return math.trunc(x / y)                   # truncate toward 0
            return float(x) / float(y)
        if o == "%":
            # §2.12 — "the remainder of the division of two integer operands"
            if not both_int:
                raise CoralError("% requires two integer operands (§2.12)", line)
            if y == 0:
                raise CoralError("division by zero in %", line)
            return math.fmod(x, y).__trunc__()
        raise CoralError(f"unknown operator {o!r}", line)

    def read_input(self, want, line):                      # §2.1
        if self.in_i >= len(self.inputs):
            raise CoralError(
                "the program asked for input but none is left — type values in "
                "the Program input box (whitespace-separated)", line)
        raw = self.inputs[self.in_i]
        self.in_i += 1
        if want in (None, "string", "character"):
            try:
                return int(raw)
            except ValueError:
                try:
                    return float(raw)
                except ValueError:
                    return raw
        try:
            if want == "integer":
                return int(raw)
            if want == "float":
                return float(raw)
            if want == "boolean":
                return raw.lower() == "true"
        except ValueError:
            raise CoralError(f"input {raw!r} is not a valid {want}", line)
        return raw

    def call(self, name, args, body, env, line=None):      # §6.1-6.2
        fn = self.funcs[name]
        _, _fname, params, rtype, rname, fbody, fline = fn
        if len(args) != len(params):
            raise CoralError(
                f"{name}() takes {len(params)} argument(s) but got {len(args)}",
                line or fline)
        local = Env()                          # functions do NOT see globals
        for (ptype, pname, is_arr), val in zip(params, args):
            if is_arr:
                local.declare(pname, ptype + "[]", val)
            else:
                local.declare(pname, ptype, coerce(ptype, val, line or fline))
        if rname:
            local.declare(rname, rtype, _zero(rtype))
        try:
            self.exec_block(fbody, local)
        except _Return as r:
            if r.value is None:
                return None
            return coerce(rtype, r.value, line or fline) if rtype else r.value
        # No explicit return: the value of the NAMED RETURN VARIABLE is what the
        # call evaluates to (§6.2 — Function ComputeSquare ... numSquared).
        return local.get(rname, fline) if rname else None


def _zero(vtype):
    return {"integer": 0, "float": 0.0, "boolean": False,
            "string": "", "character": ""}.get(vtype, 0)


def _need_num(v, line):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        art = "an" if _typename(v)[0] in "aeiou" else "a"
        raise CoralError(f"expected a number but found {art} {_typename(v)}",
                         line)


def truthy(v, line):
    if isinstance(v, bool):
        return v
    art = "an" if _typename(v)[0] in "aeiou" else "a"
    raise CoralError(f"expected a true/false condition but found {art} "
                     f"{_typename(v)}", line)


# =====================================================================
# 4. PUBLIC API
# =====================================================================
def run_coral(source, stdin=""):
    """-> {ok, output, error, steps, truncated}"""
    try:
        toks = tokenize(source)
        stmts, funcs = Parser(toks).parse_program()
    except CoralError as e:
        return {"ok": False, "output": "", "error": str(e), "steps": 0,
                "truncated": False}

    interp = Interp(stdin.split())
    try:
        interp.run(stmts, funcs)
    except CoralError as e:
        return {"ok": False, "output": interp.output(), "error": str(e),
                "steps": interp.steps, "truncated": interp.truncated}
    except _Return:
        pass
    except RecursionError:
        return {"ok": False, "output": interp.output(),
                "error": "too much recursion", "steps": interp.steps,
                "truncated": interp.truncated}
    return {"ok": True, "output": interp.output(), "error": None,
            "steps": interp.steps, "truncated": interp.truncated}
