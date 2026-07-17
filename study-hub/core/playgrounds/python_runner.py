"""Python playground backend — runs snippets in an isolated subprocess.
Local personal-study tool: isolation is best-effort (-I flag, wall-clock
timeout, output cap, scratch dir), not a hostile-code sandbox."""
import os
import subprocess
import sys
import tempfile

from . import PlaygroundBase

class PythonPlayground(PlaygroundBase):
    kind = "python"
    label = "Python console"
    stdin_enabled = True
    placeholder = ("# Python 3 \u2014 runs locally in an isolated process\n"
                   "print(2 + 3)")

    def __init__(self, timeout=4, output_cap=20000):
        self.timeout = timeout
        self.output_cap = output_cap

    def bind(self, data_dir):
        self.data_dir = data_dir
        self.scratch = os.path.join(data_dir, "pg_scratch")
        os.makedirs(self.scratch, exist_ok=True)

    def run(self, source, stdin=""):
        blocks, notes = [], []
        fd, path = tempfile.mkstemp(suffix=".py", dir=self.scratch)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(str(source))
            try:
                p = subprocess.run([sys.executable, "-I", path],
                                   input=str(stdin), capture_output=True,
                                   text=True, timeout=self.timeout,
                                   cwd=self.scratch)
            except subprocess.TimeoutExpired:
                return {"ok": False, "notes": [],
                        "blocks": [{"kind": "error",
                                    "text": f"Timed out after "
                                            f"{self.timeout}s \u2014 "
                                            "infinite loop?"}],
                        "state": {}}
            out, err = p.stdout, p.stderr
            if len(out) > self.output_cap:
                out = out[:self.output_cap]
                notes.append(f"(output truncated at "
                             f"{self.output_cap} characters)")
            if out:
                blocks.append({"kind": "text", "text": out})
            if err:
                blocks.append({"kind": "error", "text": err.strip()})
            if not out and not err:
                blocks.append({"kind": "ok", "text": "(no output)"})
            if p.returncode:
                notes.append(f"exit code {p.returncode}")
            return {"ok": p.returncode == 0, "blocks": blocks,
                    "notes": notes, "state": {}}
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def selfcheck(self):
        return [("print(2 + 3)", "", "5"),
                ("import sys\nprint(sys.stdin.read().strip().upper())",
                 "hey\n", "HEY"),
                ("print(7 // 2, 7 % 2)", "", "3 1")]
