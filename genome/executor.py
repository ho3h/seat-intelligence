"""The executor: HVM2 (pinned) runs every net. Nothing here is learned or modified."""
from __future__ import annotations
import os, re, subprocess, tempfile, time
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HVM = os.path.join(ROOT, "physics", "hvm2", "target", "release", "hvm")
HVM_DEPTH = os.path.join(ROOT, "physics", "hvm2-depth", "target", "release", "hvm")  # same rules, round scheduler
ENV = dict(os.environ, DEVELOPER_DIR="/Library/Developer/CommandLineTools")


@dataclass
class Run:
    ok: bool
    result: str = ""        # printed normal form of @main's root
    itrs: int = 0           # interactions (as counted by HVM2)
    secs: float = 0.0
    error: str = ""         # crash / timeout / hvm error text
    timed_out: bool = False
    depth: int = 0          # parallel depth (rounds) from the depth oracle
    width: int = 0          # widest round


def run_net(text: str, backend: str = "run", timeout: float = 30.0) -> Run:
    depth = backend == "depth"
    """Run a full net book (must define @main). backend: run (Rust) | run-c (C)."""
    with tempfile.NamedTemporaryFile("w", suffix=".hvm", delete=False, dir=os.path.join(ROOT, "scratch")) as f:
        f.write(text)
        path = f.name
    try:
        t0 = time.time()
        try:
            p = subprocess.run([HVM_DEPTH, "run", path] if depth else [HVM, backend, path], capture_output=True, text=True, timeout=timeout, env=ENV)
        except subprocess.TimeoutExpired:
            return Run(False, error=f"timeout after {timeout:.0f}s", timed_out=True)
        out = p.stdout
        m = re.search(r"^Result: (.*)$", out, re.M)
        it = re.search(r"^- ITRS: (\d+)", out, re.M)
        tm = re.search(r"^- TIME: ([\d.]+)s", out, re.M)
        if p.returncode != 0 or not m:
            err = (p.stderr.strip() or out.strip())[:600]
            return Run(False, error=err or f"exit {p.returncode}")
        dp = re.search(r"^- DEPTH: (\d+)", out, re.M); wd = re.search(r"^- WIDTH: (\d+)", out, re.M)
        return Run(True, m.group(1), int(it.group(1)) if it else 0, float(tm.group(1)) if tm else 0.0,
                   depth=int(dp.group(1)) if dp else 0, width=int(wd.group(1)) if wd else 0)
    finally:
        try: os.unlink(path)
        except OSError: pass


def run_native(text: str, timeout: float = 300.0, cflags=("-O3", "-mcpu=native")) -> Run:
    """Wall-clock path: HVM2 gen-c, compiled natively for arm64 with clang, run on all cores. Compile time excluded
    from `secs` (the runtime reports its own TIME); returns the runtime's interaction count and time."""
    d = tempfile.mkdtemp(dir=os.path.join(ROOT, "scratch"))
    try:
        hv = os.path.join(d, "n.hvm"); open(hv, "w").write(text)
        g = subprocess.run([HVM, "gen-c", hv], capture_output=True, text=True, env=ENV, timeout=timeout)
        if g.returncode != 0 or not g.stdout: return Run(False, error=(g.stderr or g.stdout)[:400] or "gen-c failed")
        cf = os.path.join(d, "n.c"); open(cf, "w").write(g.stdout)
        exe = os.path.join(d, "n")
        c = subprocess.run(["clang", *cflags, "-o", exe, cf, "-lpthread"], capture_output=True, text=True, timeout=timeout)
        if c.returncode != 0: return Run(False, error=c.stderr[:400])
        try: p = subprocess.run([exe], capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired: return Run(False, error=f"timeout after {timeout:.0f}s", timed_out=True)
        out = p.stdout
        m = re.search(r"^Result: (.*)$", out, re.M); it = re.search(r"^- ITRS: (\d+)", out, re.M); tm = re.search(r"^- TIME: ([\d.]+)s", out, re.M)
        if not m: return Run(False, error=(p.stderr or out)[:400])
        return Run(True, m.group(1), int(it.group(1)) if it else 0, float(tm.group(1)) if tm else 0.0)
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)
