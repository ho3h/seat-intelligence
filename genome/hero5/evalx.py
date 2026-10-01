"""HERO-5 evaluation: counterfactual worlds, exactness checking through the verified executor, delta debugging,
the kernel-aware witness extractor (generator), and English rendering."""
from __future__ import annotations
import itertools, time, threading
from collections import deque
from .core import Problem, greedy_log, prog, run_net, assemble, decode

# ------------------------------------------------------------------ oracle: counterfactual worlds
class Oracle:
    """D holds in the world made of fact set S (plus the subject row).  Runs the verified net (and checks the reference agrees)."""
    def __init__(self, pr: Problem, dec: dict, use_net=True):
        self.pr, self.dec, self.use_net = pr, dec, use_net
        self.calls_net = 0; self.calls_ref = 0; self.secs_net = 0.0; self.mismatch = 0; self.cache = {}; self.log = []
        self.P, self.book = prog()

    def world(self, S):
        pr, d = self.pr, self.dec
        S = set(S)
        if d["subject"] is not None: S.add(d["subject"])
        edges = [pr.edges[k] for k in sorted(S) if k < pr.E]
        mnl = [pr.mnl[k - pr.E] for k in sorted(S) if pr.E <= k < pr.E + pr.M]
        ids = sorted({x for e in edges for x in e[:2]} | {x for m in mnl for x in m} | {d["a"], d["b"]})
        mp = {x: i for i, x in enumerate(ids)}
        cap = pr.cap if pr.cap_fact in S else len(ids) + 1
        return (len(ids), cap, [(mp[x], mp[y]) for x, y in mnl], [(mp[u], mp[v], s) for u, v, s in edges]), mp[d["a"]], mp[d["b"]]

    def _decide(self, labels, a, b):
        return labels[a] == labels[b] if self.dec["polarity"] == "same" else labels[a] != labels[b]

    def ref(self, S):
        x, a, b = self.world(S)
        self.calls_ref += 1
        return self._decide(greedy_log(*x)[0], a, b)

    def replay_on_net(self):
        """Run every world this oracle was asked about (in order) through the executor; returns (calls, seconds)."""
        t0 = time.time(); n = 0
        for key in self.log:
            x, a, b = self.world(key)
            res = run_net(assemble(self.P, self.book, x), "run", 300)
            if not res.ok: raise RuntimeError("net failed: " + res.error)
            n += 1
        return n, time.time() - t0

    def __call__(self, S):
        key = frozenset(S)
        if key in self.cache: return self.cache[key]
        self.log.append(key)
        x, a, b = self.world(S)
        r = self._decide(greedy_log(*x)[0], a, b)
        if self.use_net:
            t0 = time.time()
            res = run_net(assemble(self.P, self.book, x), "run", 300)
            self.secs_net += time.time() - t0; self.calls_net += 1
            if not res.ok: raise RuntimeError("net failed: " + res.error)
            got = decode(res.result, self.P.out)
            if got != greedy_log(*x)[0]: self.mismatch += 1
            r = self._decide(got, a, b)
        self.cache[key] = r
        return r


# ------------------------------------------------------------------ delta debugging (ddmin), over a list of facts
def ddmin(U, test):
    U = list(U); cur = list(U); n = 2
    if not test(cur): return None
    if test([]): return []
    while len(cur) >= 2:
        size = max(1, len(cur) // n)
        chunks = [cur[i:i + size] for i in range(0, len(cur), size)]
        red = False
        for c in chunks:
            if test(c): cur, n, red = c, 2, True; break
        if not red:
            for c in chunks:
                comp = [x for x in cur if x not in c]
                if comp and test(comp): cur, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(cur): break
            n = min(len(cur), 2 * n)
    # final single-fact pass (1-minimality)
    changed = True
    while changed:
        changed = False
        for x in list(cur):
            comp = [y for y in cur if y != x]
            if test(comp): cur = comp; changed = True; break
    return cur


# ------------------------------------------------------------------ logged greedy over a subset of rows (original ids)
def greedy_rows(pr: Problem, S, subject, ):
    """Reference greedy on the rows in S (+ subject), original record ids, no compression.  Returns per-row outcome and the
    processing position, so a witness can be read off the merge log."""
    S = set(S)
    if subject is not None: S.add(subject)
    rows = [(k, *pr.edges[k]) for k in sorted(S) if k < pr.E]
    mnl = [(k, *pr.mnl[k - pr.E]) for k in sorted(S) if pr.E <= k < pr.E + pr.M]
    cap = pr.cap if pr.cap_fact in S else None
    order = sorted(rows, key=lambda r: (-r[3], r[1], r[2]))
    p = {}; mem = {}
    def find(x):
        while p.get(x, x) != x: x = p[x]
        return x
    out = {}
    for pos, (k, u, v, s) in enumerate(order):
        a, b = find(u), find(v)
        if a == b: out[k] = dict(kind="noop", pos=pos); continue
        A, B = mem.get(a, frozenset([a])), mem.get(b, frozenset([b]))
        blk = [(mk, x, y) for (mk, x, y) in mnl if (x in A and y in B) or (x in B and y in A)]
        capbad = cap is not None and len(A) + len(B) > cap
        if blk or capbad:
            out[k] = dict(kind="skip", pos=pos, blk=blk, capbad=capbad, A=A, B=B); continue
        out[k] = dict(kind="merge", pos=pos); p[a] = b; mem[b] = A | B; mem.pop(a, None)
    return out, {k: (u, v) for k, u, v, s in rows}


def _bfs_path(adj, src, dst):
    """shortest path of edge ids from src to dst in adj {node: [(nbr, k)]}; deterministic."""
    if src == dst: return []
    prev = {src: None}; dq = deque([src])
    while dq:
        x = dq.popleft()
        for y, k in sorted(adj.get(x, []), key=lambda t: (t[0], t[1])):
            if y in prev: continue
            prev[y] = (x, k)
            if y == dst:
                path = []; z = y
                while prev[z] is not None: z, kk = prev[z][0], prev[z][1]; path.append(kk)
                return path[::-1]
            dq.append(y)
    return None


def extract(pr: Problem, dec: dict, C):
    """Kernel-aware witness extraction from a causal set C (one logged reference simulation on the rows in C; no net runs).
    Returns (witness fact set, claimed reason, roles) or (set(C), 'fallback', None) when C does not reproduce the decision."""
    subj = dec["subject"]
    out, ends = greedy_rows(pr, C, subj)
    def tree_adj(before_pos):
        adj = {}
        for k, o in out.items():
            if o["kind"] == "merge" and o["pos"] < before_pos:
                u, v = ends[k]; adj.setdefault(u, []).append((v, k)); adj.setdefault(v, []).append((u, k))
        return adj
    if dec["polarity"] == "same":
        a, b = dec["a"], dec["b"]
        adj = tree_adj(10 ** 9)
        path = _bfs_path(adj, a, b)
        if path is None: return set(C), "fallback", None
        return set(path), "merge", dict(path=path)
    o = out[subj]
    if o["kind"] != "skip": return set(C), "fallback", None
    u, v = dec["a"], dec["b"]
    adj = tree_adj(o["pos"])
    A, B = o["A"], o["B"]
    if o["blk"]:
        best = None
        for (mk, x, y) in o["blk"]:
            x1, y1 = (x, y) if x in A else (y, x)          # x1 in u's cluster A? A is the cluster of u
            # A is the cluster containing u (find(u)); B the cluster of v
            if u in A: ax, by = x1, y1
            else: ax, by = y1, x1
            pa = _bfs_path(adj, u, ax); pb = _bfs_path(adj, v, by)
            if pa is None or pb is None: continue
            cost = (len(pa) + len(pb), mk)
            if best is None or cost < best[0]: best = (cost, mk, pa, pb, (ax, by))
        if best is None: return set(C), "fallback", None
        _, mk, pa, pb, xy = best
        return {subj, mk} | set(pa) | set(pb), "mnl", dict(mnl=mk, pa=pa, pb=pb, xy=xy)
    if o["capbad"]:
        # grow connected sub-clusters around u and v (BFS in the merge tree, alternately) until they exceed the cap
        need = pr.cap + 1
        def bfs_order(src):
            seen = {src}; dq = deque([src]); seq = []      # (node, edge used to reach it)
            seq.append((src, None))
            while dq:
                x = dq.popleft()
                for y, k in sorted(adj.get(x, []), key=lambda t: (t[0], t[1])):
                    if y in seen: continue
                    seen.add(y); dq.append(y); seq.append((y, k))
            return seq
        sa, sb = bfs_order(u), bfs_order(v)
        ia = ib = 1; edges = set(); turn = 0
        while ia + ib < need:
            if turn == 0 and ia < len(sa): edges.add(sa[ia][1]); ia += 1
            elif ib < len(sb): edges.add(sb[ib][1]); ib += 1
            elif ia < len(sa): edges.add(sa[ia][1]); ia += 1
            else: break
            turn ^= 1
        if ia + ib < need: return set(C), "fallback", None
        return {subj, pr.cap_fact} | edges, "cap", dict(edges=sorted(edges), sizes=(ia, ib))
    return set(C), "fallback", None


# ------------------------------------------------------------------ exactness classification
def claimed_reason(pr, E):
    hasm = any(pr.E <= k < pr.E + pr.M for k in E); hasc = pr.cap_fact in E
    return "both" if hasm and hasc else "mnl" if hasm else "cap" if hasc else "none"


def truth_reason(dec):
    return "merge" if dec["polarity"] == "same" else dec["reason"]


def classify(pr: Problem, dec: dict, E, orc: Oracle, exhaustive_max=14, net_all_max=60):
    """E: set of fact ids (subject excluded).  Returns dict with S,N,M,F, class and evidence."""
    E = sorted(set(E) - ({dec["subject"]} if dec["subject"] is not None else set()))
    res = dict(size=len(E), claimed=claimed_reason(pr, E))
    S = orc(E)                                           # sufficiency (net)
    res["S"] = bool(S)
    trace = []
    if not S:
        tr = truth_reason(dec)
        if dec["polarity"] == "same" or not E: cls = "incomplete"     # an empty explanation names nothing, so it cannot be wrong
        else: cls = "incomplete" if res["claimed"] in (tr, "both", "none") else "wrong"   # wrong = names the OTHER reason
        res.update(cls=cls, N=None, M=None, F=None, redundant=[])
        return res
    # necessity of each fact by deletion (through the net); stop at the first redundant fact when the set is large
    redundant = []
    for f in E:
        if not orc([g for g in E if g != f]): continue
        redundant.append(f)
        if len(E) > net_all_max: break
    res["redundant"] = redundant
    res["N"] = not redundant
    # minimality: exhaustive over proper subsets (reference) when small
    if redundant: res["M"] = False
    elif len(E) <= exhaustive_max:
        ok = True
        for r in range(0, len(E)):
            for sub in itertools.combinations(E, r):
                if orc.ref(sub): ok = False; break
            if not ok: break
        res["M"] = ok
    else:
        res["M"] = True; res["M_note"] = "1-minimal only (too large to enumerate)"
    # faithfulness (merge decisions): D still holds with every blocking clause present
    if dec["polarity"] == "same":
        allblk = set(E) | set(range(pr.E, pr.E + pr.M + 1))
        res["F"] = bool(orc(allblk))
    else:
        res["F"] = True
    if res["N"] and res["M"] and res["F"]: cls = "exact"
    elif res["N"] and res["M"] and not res["F"]: cls = "wrong"
    else: cls = "over-inclusive"
    res["cls"] = cls
    return res


# ------------------------------------------------------------------ English rendering
def _who(pr, x):
    return pr.names.get(x) or pr.names.get(str(x)) or f"record {x}"


def _rel(pr, k, hero):
    u, v, s = pr.edges[k]
    return f"{_who(pr, u)}-{_who(pr, v)} (score {s})"


def render(pr: Problem, dec: dict, E, roles=None, mode="witness"):
    u, v = dec["a"], dec["b"]
    if roles and roles.get("path") is not None:
        chain = ", ".join(_rel(pr, k, True) for k in roles["path"])
        return f"{_who(pr, u)} sits with {_who(pr, v)} because each link in the chain was accepted and merged in priority order: {chain}."
    if roles and "mnl" in roles:
        x, y = roles["xy"]
        def end(z, w, path):      # z: the rule's end, w: the subject's end it must be joined to
            if z == w: return f"{_who(pr, w)} is itself one end of that rule"
            via = ", ".join(_rel(pr, k, True) for k in path)
            return f"{_who(pr, z)} was already seated with {_who(pr, w)} via {via}"
        ss = pr.edges[dec["subject"]][2]; ps = [pr.edges[k][2] for k in roles["pa"] + roles["pb"]]
        order = (f" Those links were settled first (scores {', '.join(map(str, ps))} against this pair's {ss}; equal scores go by id order)." if ps else "")
        return (f"{_who(pr, u)} was kept out of {_who(pr, v)}'s section because the must-not-link rule forbids {_who(pr, x)} with "
                f"{_who(pr, y)}: {end(x, u, roles['pa'])}, and {end(y, v, roles['pb'])}.{order}")
    if roles and "edges" in roles:
        a, b = roles["sizes"]
        return (f"{_who(pr, u)} was kept out of {_who(pr, v)}'s section because the size limit of {pr.cap} would be exceeded: "
                f"{a} {'guests' if pr.names else 'records'} already with {_who(pr, u)} plus {b} already with {_who(pr, v)} is more than {pr.cap}.")
    return f"({dec['kind']}) the causal set names {len(E)} facts; no structure recovered."
