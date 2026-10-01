"""HERO-5 core: the reconciliation kernel with provenance, the annotated-input encoder, the tracer driver.

A Problem is the input of the verified net runs/exp18/t5_conflict_greedy_cap.hvm:  (n, cap, mnl, cands).
FACTS (the units an explanation may name):  edge rows 0..E-1 (in list order), must-not-link rows E..E+M-1, then the cap
clause (fact id E+M).  n (the record count) is structure, not a fact.
"""
from __future__ import annotations
import os, re, subprocess, sys, time, tempfile, itertools
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.corpus import load_all
from genome.verify import assemble
from genome.executor import run_net, ENV
from genome.types import decode

TRACER = os.path.join(ROOT, "genome", "hero5", "tracer", "target", "release", "hvm")
NET_LABELS = os.path.join(ROOT, "runs", "exp18", "t5_conflict_greedy_cap.hvm")
_P = None
_BOOK = None


def prog():
    global _P, _BOOK
    if _P is None:
        _P = load_all()["t5_conflict_greedy_cap"]
        _BOOK = open(NET_LABELS).read()
    return _P, _BOOK


@dataclass
class Problem:
    n: int
    cap: int
    mnl: list          # [(a, b)] a < b
    edges: list        # [(u, v, score)] u < v, distinct (u, v)
    name: str = ""
    names: dict = field(default_factory=dict)   # record id -> display name (hero data)

    @property
    def E(self): return len(self.edges)
    @property
    def M(self): return len(self.mnl)
    @property
    def F(self): return self.E + self.M + 1
    @property
    def cap_fact(self): return self.E + self.M

    def as_input(self): return (self.n, self.cap, list(self.mnl), list(self.edges))


# ------------------------------------------------------------------ reference greedy with a full log
def greedy_log(n, cap, mnl, edges):
    """Same semantics as genome.corpus.t5_b._greedy.  Returns labels and, per edge index (input order), an outcome dict:
       kind in {'merge','noop','skip'}, for skip: mnl_bad, cap_bad, blocker (x,y) or None, A, B (member sets at that time);
       for merge: A, B.  Also 'order': edge indices in processing order."""
    order = sorted(range(len(edges)), key=lambda i: (-edges[i][2], edges[i][0], edges[i][1]))
    p = list(range(n)); mem = {i: {i} for i in range(n)}
    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]; x = p[x]
        return x
    out = {}
    for i in order:
        u, v, _ = edges[i]
        a, b = find(u), find(v)
        if a == b:
            out[i] = dict(kind="noop"); continue
        A, B = mem[a], mem[b]
        blk = None
        for (x, y) in mnl:
            if (x in A and y in B) or (x in B and y in A): blk = (x, y); break
        capbad = cap is not None and len(A) + len(B) > cap
        if blk is not None or capbad:
            out[i] = dict(kind="skip", mnl_bad=blk is not None, cap_bad=capbad, blocker=blk, A=frozenset(A), B=frozenset(B))
            continue
        out[i] = dict(kind="merge", A=frozenset(A), B=frozenset(B))
        p[a] = b; mem[b] = A | B; del mem[a]
    top = {r: max(s) for r, s in mem.items()}
    labels = [top[find(i)] for i in range(n)]
    return labels, out, order


def labels_of(n, cap, mnl, edges):
    return greedy_log(n, cap, mnl, edges)[0]


# ------------------------------------------------------------------ traced-input encoder
CHUNK = 1000


def _list_text(refs, defs, tag):
    """refs: list of tree texts (already strings).  Returns root text, appends spill defs."""
    chunks = [refs[i:i + CHUNK] for i in range(0, len(refs), CHUNK)] or [[]]
    tail = "(0 *)"
    for i in range(len(chunks) - 1, -1, -1):
        body = "".join(f"(1 ({x} " for x in chunks[i]) + tail + "))" * len(chunks[i])
        if i == 0: return body
        name = f"__h5{tag}_{i}"
        defs.append(f"@{name} = {body}")
        tail = f"@{name}"


def traced_main(pr: Problem):
    """Book text (main + fact defs + spill defs) for the annotated input.  Row k is the definition @fact_k, so the
    tracer can seed its taint set with {k} when the row is instantiated.  Same value as genome.types.encode."""
    defs = []
    for k, (u, v, s) in enumerate(pr.edges): defs.append(f"@fact_{k} = ({u} ({v} {s}))")
    for j, (a, b) in enumerate(pr.mnl): defs.append(f"@fact_{pr.E + j} = ({a} {b})")
    defs.append(f"@fact_{pr.cap_fact} = {pr.cap}")
    cs = _list_text([f"@fact_{k}" for k in range(pr.E)], defs, "c")
    ml = _list_text([f"@fact_{pr.E + j}" for j in range(pr.M)], defs, "m")
    main = f"@main = r\n  & @prog ~ (({pr.n} (@fact_{pr.cap_fact} ({ml} {cs}))) r)\n"
    return main + "\n" + "\n".join(defs) + "\n"


def traced_book(pr: Problem):
    _, book = prog()
    return traced_main(pr) + "\n" + book + "\n"


# ------------------------------------------------------------------ running
def _tmp(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".hvm", delete=False, dir=os.path.join(ROOT, "scratch"))
    f.write(text); f.close(); return f.name


def parse_stats(out):
    st = {}
    for k in ("ITRS", "DEPTH", "WIDTH", "WORK", "TSETS", "TUNIONS", "TMEMOHITS", "TMEMOSIZE", "TWORDS"):
        m = re.search(rf"^- {k}: (\d+)", out, re.M)
        if m: st[k.lower()] = int(m.group(1))
    m = re.search(r"^- TIME: ([\d.]+)s", out, re.M)
    if m: st["secs"] = float(m.group(1))
    return st


def run_traced(pr: Problem, mode=2, timeout=3600):
    """Run the tracer on the annotated input.  Returns (tokens, sets, stats)."""
    path = _tmp(traced_book(pr))
    try:
        env = dict(ENV, GENOME_TR=str(mode), GENOME_TR_F=str(pr.F))
        t0 = time.time()
        p = subprocess.run([TRACER, "run", path], capture_output=True, text=True, timeout=timeout, env=env)
        wall = time.time() - t0
    finally:
        os.unlink(path)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-500:] or p.stdout[-500:])
    out = p.stdout
    st = parse_stats(out); st["wall"] = wall
    m = re.search(r"^TOKENS (.*)$", out, re.M)
    toks = m.group(1).split() if m else []
    sets = {}
    for mm in re.finditer(r"^SET (\d+) ?(.*)$", out, re.M):
        sets[int(mm.group(1))] = frozenset(int(x) for x in mm.group(2).split(",") if x)
    return toks, sets, st


def run_untraced_same_book(pr: Problem, timeout=3600):
    """Depth oracle (unmodified physics/hvm2-depth) on the very same annotated book: baseline for overhead."""
    from genome.executor import HVM_DEPTH
    path = _tmp(traced_book(pr))
    try:
        t0 = time.time()
        p = subprocess.run([HVM_DEPTH, "run", path], capture_output=True, text=True, timeout=timeout, env=ENV)
        wall = time.time() - t0
    finally:
        os.unlink(path)
    st = parse_stats(p.stdout); st["wall"] = wall
    return st


def run_untraced_plain(pr: Problem, backend="depth", timeout=3600):
    P, book = prog()
    t0 = time.time()
    r = run_net(assemble(P, book, pr.as_input()), backend, timeout)
    return dict(itrs=r.itrs, depth=r.depth, secs=r.secs, wall=time.time() - t0, ok=r.ok, result=r.result)


# ------------------------------------------------------------------ token stream -> tree -> labels with taints
def parse_tokens(toks):
    """Preorder stream -> arrays.  Returns (kind[], val[], taint[], kids[]) ; node 0 is root."""
    kind, val, tnt, kids = [], [], [], []
    stack = []   # (node index, children still expected)
    for tk in toks:
        if tk == "V":
            k, v, t, arity = "V", 0, 0, 0
        else:
            head, t = tk.rsplit(":", 1); t = int(t)
            c = head[0]
            if c == "N": k, v, arity = "N", int(head[1:]), 0
            elif c == "E": k, v, arity = "E", 0, 0
            elif c == "R": k, v, arity = "R", head[1:], 0
            else: k, v, arity = c, 0, 2
        idx = len(kind); kind.append(k); val.append(v); tnt.append(t); kids.append([])
        if stack:
            pi, rem = stack[-1]; kids[pi].append(idx)
            if rem - 1 == 0: stack.pop()
            else: stack[-1] = (pi, rem - 1)
        if arity: stack.append((idx, arity))
    return kind, val, tnt, kids


def list_elems(tree, sets, elem_walk=None):
    """Walk a Cons/Nil list root.  Returns [(value_tree_nodes, taint_set)] where taint = tag + payload + head subtree
    (NOT the spine before it)."""
    kind, val, tnt, kids = tree
    out = []
    cur = 0
    while True:
        if kind[cur] != "C": raise ValueError("expected list cell, got " + kind[cur])
        tag, pay = kids[cur]
        if kind[tag] != "N": raise ValueError("bad tag")
        if val[tag] == 0: break
        head, tail = kids[pay]
        # gather head subtree
        st = [head]; sub = []
        while st:
            x = st.pop(); sub.append(x); st.extend(kids[x])
        ids = {tnt[cur], tnt[tag], tnt[pay]} | {tnt[x] for x in sub}
        ts = frozenset().union(*[sets[i] for i in ids])
        out.append((head, ts))
        cur = tail
    return out


def traced_labels(pr: Problem, mode=2):
    toks, sets, st = run_traced(pr, mode)
    tree = parse_tokens(toks)
    els = list_elems(tree, sets)
    labels = [tree[1][h] for h, _ in els]
    taints = [ts for _, ts in els]
    return labels, taints, st
