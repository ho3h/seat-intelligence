"""Swing 20 runner: OpenSanctions slice -> tree-shaped input -> net -> exact check against Python union-find.

usage: python3 -m genome.exp16.run <mode> N [N ...]
  modes: rust (Rust interpreter + digest, correctness + wall clock), depth (depth oracle, bare program),
         native (arm64 C runtime, book passed as DATA to a precompiled interpreter; see hvmc_main.c), ref (Python only)
Results are appended as JSON lines to runs/exp16/results.jsonl.
"""
from __future__ import annotations
import json, os, re, subprocess, sys, time, tempfile
from .data import slice_, uf_components
from .net import build
from ..digest import gen_digest, py_digest
from ..types import tup, u24, list_of, decode

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HVM = os.path.join(ROOT, "physics/hvm2/target/release/hvm")
HVM_DEPTH = os.path.join(ROOT, "physics/hvm2-depth/target/release/hvm")
OUT_T = tup(list_of(u24), list_of(tup(u24, u24, u24)))
OUT_FULL = tup(list_of(u24), list_of(tup(u24, u24, u24)), list_of(tup(u24, u24)))
RUNS = os.path.join(ROOT, "runs/exp16")
DRIVER_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hvmc_main.c")
ENV = dict(os.environ, DEVELOPER_DIR="/Library/Developer/CommandLineTools")
CH = 512           # edge leaves per input chunk definition (about 1.5k nodes, under the 4095-node cap)


# ---------------------------------------------------------------- reference
def reference(s):
    n, tau = s["n"], s["tau"]
    root = uf_components(n, [(u, v) for u, v, sc in s["edges"] if sc >= tau])
    big = {}
    for i, r in enumerate(root): big[r] = max(big.get(r, -1), i)
    canon = [big[root[i]] for i in range(n)]
    conf = [(a, b, canon[a]) for a, b in s["mnl"] if canon[a] == canon[b]]
    return canon, conf


def reference_full(s):
    """Expected output of the end-to-end net: (canon after the greedy, conflicts, skipped merges grouped by LP label)."""
    canon, conf = reference(s)
    g, sk = greedy_mnl(s)
    sk = sorted(sk, key=lambda e: (canon[e[0]], PROC[id(s)][e]))
    return g, conf, sk


PROC = {}


def greedy_mnl(s):
    """RECONCILIATION-SPEC step 4 reference (no size cap): accepted merges by descending score, ties ascending (u, v);
    a merge is skipped if it would put both ends of a must-not-link pair in one cluster. Returns (canon, skipped)."""
    n, tau = s["n"], s["tau"]
    par = list(range(n)); members = {i: {i} for i in range(n)}
    mnl = {}
    for a, b in s["mnl"]:
        mnl.setdefault(a, set()).add(b); mnl.setdefault(b, set()).add(a)
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    skipped = []
    proc = sorted((e for e in s["edges"] if e[2] >= tau), key=lambda e: (-e[2], e[0], e[1]))
    PROC[id(s)] = {(u, v): i for i, (u, v, sc) in enumerate(proc)}
    for u, v, sc in proc:
        ru, rv = find(u), find(v)
        if ru == rv: continue
        A, B = members[ru], members[rv]
        if len(A) > len(B): A, B = B, A
        if any(y in B for x in A for y in mnl.get(x, ())):
            skipped.append((u, v)); continue
        par[ru] = rv; members[rv] = members[ru] | members[rv]; del members[ru]
    big = {}
    for i in range(n): r = find(i); big[r] = max(big.get(r, -1), i)
    return [big[find(i)] for i in range(n)], skipped


def lp_stats(s):
    """LP rounds R (max-label propagation until stable) and max degree over accepted edges."""
    n = s["n"]; adj = [[] for _ in range(n)]
    for u, v, sc in s["edges"]:
        if sc >= s["tau"]: adj[u].append(v); adj[v].append(u)
    lab = list(range(n)); r = 0
    while True:
        new = [max([lab[i]] + [lab[j] for j in adj[i]]) for i in range(n)]
        if new == lab: break
        lab = new; r += 1
    return dict(lp_rounds=r, max_deg=max(len(a) for a in adj))


# ---------------------------------------------------------------- encoding
def _perfect(items, pad):
    h = 0
    while (1 << h) < max(1, len(items)): h += 1
    return items + [pad] * ((1 << h) - len(items)), h


def tree_text(items, defs, tag):
    """Perfect binary tree of CONs over items (texts). Subtrees of CH or CH*1024^j leaves spill into definitions, so
    every definition stays under the node cap and the text nesting (parser recursion) stays ~log2(CH) + 1 deep."""
    def go(lo, hi):
        if hi - lo == 1: return items[lo]
        mid = (lo + hi) // 2
        t = f"({go(lo, mid)} {go(mid, hi)})"
        size = hi - lo
        if size >= CH and (size // CH) & ((size // CH) - 1) == 0 and (size.bit_length() - CH.bit_length()) % 10 == 0:
            name = f"__{tag}{len(defs)}"
            defs.append(f"@{name} = {t}")
            return f"@{name}"
        return t
    return go(0, len(items))


def encode_input(s, by_score=False):
    """by_score: lay the edge tree out in processing order (descending score, ties ascending (u, v)); the full net's
    greedy relies on it. Otherwise ascending (u, v)."""
    n, tau = s["n"], s["tau"]
    L = max(1, (n - 1).bit_length())
    edges = sorted(s["edges"], key=lambda e: (-e[2], e[0], e[1])) if by_score else s["edges"]
    E, HE = _perfect([f"({u} ({v} {sc}))" for u, v, sc in edges], "(0 (1 0))")
    M, HM = _perfect([f"({a} ({b} 1))" for a, b in s["mnl"]], "(0 (0 0))")
    defs = []
    et = tree_text(E, defs, "e"); mt = tree_text(M, defs, "m")
    return f"({n} ({L} ({tau} ({et} ({HE} ({mt} {HM}))))))", defs, dict(L=L, HE=HE, HM=HM)


def book(s, net, digest=True, full=False):
    root, defs, meta = encode_input(s, by_score=full)
    if digest:
        dbook, droot = gen_digest(OUT_FULL if full else OUT_T)
        main = f"@main = r\n  & @prog ~ ({root} o)\n  & @{droot} ~ (o ((0 0) r))\n"
    else:
        dbook, main = "", f"@main = r\n  & @prog ~ ({root} r)\n"
    return main + "\n" + "\n".join(defs) + "\n\n" + net + "\n\n" + dbook, meta


# ---------------------------------------------------------------- executors
def _timed(cmd, timeout):
    """Run under /usr/bin/time -l with the stack soft limit raised to the hard limit; returns (stdout, stderr, secs, rss)."""
    sh = f"ulimit -s hard; exec /usr/bin/time -l {' '.join(cmd)}"
    t = time.time()
    p = subprocess.run(["/bin/bash", "-c", sh], capture_output=True, text=True, timeout=timeout, env=ENV)
    wall = time.time() - t
    m = re.search(r"(\d+)\s+maximum resident set size", p.stderr)
    return p.stdout, p.stderr, wall, int(m.group(1)) if m else 0


def _parse(out):
    g = lambda pat, f=int: (lambda m: f(m.group(1)) if m else None)(re.search(pat, out, re.M))
    return dict(result=g(r"^Result: (.*)$", str), itrs=g(r"^- ITRS: (\d+)"), time=g(r"^- TIME: ([\d.]+)s", float),
                depth=g(r"^- DEPTH: (\d+)"), width=g(r"^- WIDTH: (\d+)"))


def driver():
    tpc = os.environ.get("TPC_L2", "3")      # 2^TPC_L2 worker threads (3 = 8 threads; the machine is shared)
    exe = os.path.join(RUNS, f"hvmc_arm64_t{tpc}")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(DRIVER_SRC):
        subprocess.run(["arch", "-arm64", "clang", "-arch", "arm64", "-O3", "-mcpu=native", f"-DTPC_L2={tpc}", "-I", os.path.join(ROOT, "physics/hvm2/src"),
                        "-o", exe, DRIVER_SRC, "-lpthread", "-lm"], check=True, env=ENV)
    return exe


def book_buffer(text, path):
    """Serialise the book exactly as HVM2's run-c does (Book::to_buffer), taken from `hvm gen-c`'s BOOK_BUF, to a file."""
    with tempfile.NamedTemporaryFile("w", suffix=".hvm", delete=False, dir=os.path.join(ROOT, "scratch")) as f:
        f.write(text); hv = f.name
    try:
        p = subprocess.run([HVM, "gen-c", hv], capture_output=True, text=True, env=ENV, timeout=1800)
    finally:
        os.unlink(hv)
    m = re.search(r"^static const u8 BOOK_BUF\[\] = \{([^}]*)\};", p.stdout, re.M)
    if not m: raise RuntimeError("gen-c gave no BOOK_BUF: " + p.stderr[:300])
    data = bytes(int(x) for x in m.group(1).split(","))
    open(path, "wb").write(data)
    return len(data)


def run(mode, N, net_text, timeout=3600, full=False):
    s = slice_(N)
    t0 = time.time(); canon, conf = reference(s); t_ref = time.time() - t0
    rec = dict(mode=mode, N=N, n=s["n"], m_edges=len(s["edges"]), accepted=sum(1 for e in s["edges"] if e[2] >= s["tau"]),
               mnl=len(s["mnl"]), gold=len(s["gold"]), conflicts_ref=len(conf), py_uf_secs=round(t_ref, 3))
    rec.update(lp_stats(s))
    if full:
        g, conf2, sk = reference_full(s)
        want = py_digest((g, conf2, sk), OUT_FULL); rec["skipped_ref"] = len(sk)
    else:
        want = py_digest((canon, conf), OUT_T)
    if mode == "ref":
        return rec
    text, meta = book(s, net_text, digest=(mode != "depth"), full=full); rec.update(meta)
    rec["book_bytes"] = len(text)
    path = os.path.join(ROOT, "scratch", f"exp16_{mode}_{N}_{os.getpid()}.hvm")
    open(path, "w").write(text)
    try:
        if mode == "rust":
            out, err, wall, rss = _timed([HVM, "run", path], timeout)
        elif mode == "depth":
            out, err, wall, rss = _timed([HVM_DEPTH, "run", path], timeout)
        elif mode == "native":
            exe = driver(); buf = path + ".bin"
            t = time.time(); rec["buf_bytes"] = book_buffer(text, buf); rec["serialise_secs"] = round(time.time() - t, 1)
            out, err, wall, rss = _timed(["arch", "-arm64", exe, buf], timeout)
            os.unlink(buf)
    finally:
        os.unlink(path)
    r = _parse(out)
    rec.update(itrs=r["itrs"], rt_secs=r["time"], wall=round(wall, 2), max_rss_mb=round(rss / 2**20, 1),
               depth=r["depth"], width=r["width"])
    if mode == "depth":
        rec["ok_run"] = r["depth"] is not None
        if not rec["ok_run"]: rec["err"] = (err or out)[-400:]
    else:
        try:
            got = decode(r["result"], tup(u24, u24)) if r["result"] else None
        except Exception as e:
            got = f"undecodable: {e}"
        rec["correct"] = got == want
        if not rec["correct"]: rec["err"] = f"got {got} want {want} :: " + (err or out)[-400:]
    return rec


if __name__ == "__main__":
    mode = sys.argv[1]
    variant = os.environ.get("NET", "list")
    if variant == "full":
        from .net_full import build as build_full
        net = build_full(int(os.environ.get("K", "2")))
    else:
        net = build(int(os.environ.get("K", "2")), variant)
    for N in map(int, sys.argv[2:]):
        rec = dict(net=variant, tpc_l2=int(os.environ.get("TPC_L2", "3")) if mode == "native" else None, **run(mode, N, net, full=(variant == "full")))
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "results.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
