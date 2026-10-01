"""T3 Graph algorithms, part A (25 programs): reachability, traversal, distances, components, cycles, orders, degrees.

Graph encoding: an input is a tuple whose first element is n (vertices are 0..n-1), then any scalar arguments,
then the edge list LAST as a list of (u, v) pairs. Unreachable / undefined distances are 16777215."""
import heapq
from collections import deque
from . import program
from ..types import u24, list_of, tup, MASK

M = MASK
BIG = MASK  # 16777215
L = list_of(u24)
E = list_of(tup(u24, u24))
G = tup(u24, E)                 # (n, edges)
GS = tup(u24, u24, E)           # (n, s, edges)
GST = tup(u24, u24, u24, E)     # (n, s, t, edges)
S = list(range(0, 9))
S1 = list(range(1, 9))
TS = [64, 128]

UND = ("The graph is UNDIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of undirected "
       "edges (u, v) with u < n, v < n and u != v; each edge appears exactly once, in either orientation ((u, v) and "
       "(v, u) denote the same edge and never both appear), there are no self loops, and the order of the list is "
       "arbitrary. ")
DIR = ("The graph is DIRECTED: n is the number of vertices, numbered 0..n-1, and edges is a list of directed edges "
       "(u, v) meaning an edge from u to v, with u < n, v < n and u != v; no ordered pair appears twice (u->v and "
       "v->u may both be present), there are no self loops, and the order of the list is arbitrary. ")


# ---------------------------------------------------------------- validity
def und_ok(n, es):
    if any(not (u < n and v < n and u != v) for u, v in es): return False
    return len({(min(u, v), max(u, v)) for u, v in es}) == len(es)


def dir_ok(n, es):
    if any(not (u < n and v < n and u != v) for u, v in es): return False
    return len(set(es)) == len(es)


def is_dag(n, es):
    return dir_ok(n, es) and len(_kahn(n, es)) == n


# ---------------------------------------------------------------- helpers
def uadj(n, es):
    a = [[] for _ in range(n)]
    for u, v in es:
        a[u].append(v); a[v].append(u)
    for l in a: l.sort()
    return a


def dadj(n, es):
    a = [[] for _ in range(n)]
    for u, v in es: a[u].append(v)
    for l in a: l.sort()
    return a


def bfs(adj, s):
    d = [BIG] * len(adj); d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] == BIG: d[v] = d[u] + 1; q.append(v)
    return d


def comps(adj, skip=None):
    """Component label (smallest vertex id) per vertex; skipped vertex gets None."""
    lab = [None] * len(adj)
    for s in range(len(adj)):
        if s == skip or lab[s] is not None: continue
        lab[s] = s; st = [s]
        while st:
            u = st.pop()
            for v in adj[u]:
                if v != skip and lab[v] is None: lab[v] = s; st.append(v)
    return lab


def ncomps(adj, skip=None):
    return sum(1 for v, l in enumerate(comps(adj, skip)) if l == v)


def reach_sets(n, es):
    a = dadj(n, es)
    return [{v for v, d in enumerate(bfs(a, s)) if d != BIG} for s in range(n)]


def _kahn(n, es):
    a = dadj(n, es); indeg = [0] * n
    for _, v in es: indeg[v] += 1
    h = [v for v in range(n) if indeg[v] == 0]; heapq.heapify(h); out = []
    while h:
        u = heapq.heappop(h); out.append(u)
        for v in a[u]:
            indeg[v] -= 1
            if indeg[v] == 0: heapq.heappush(h, v)
    return out


def scc_labels(n, es):
    r = reach_sets(n, es)
    return [min(u for u in range(n) if v in r[u] and u in r[v]) for v in range(n)]


def two_colour(n, es):
    a = uadj(n, es); c = [None] * n
    for s in range(n):
        if c[s] is not None: continue
        c[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in a[u]:
                if c[v] is None: c[v] = 1 - c[u]; q.append(v)
                elif c[v] == c[u]: return None
    return c


# ---------------------------------------------------------------- generators
def _norm_und(rng, es):
    es = [(min(u, v), max(u, v)) for u, v in es]
    es = list(dict.fromkeys(es)); rng.shuffle(es)
    return es


def _rand_pairs(rng, n, m, directed, ok=lambda u, v: True):
    maxm = n * (n - 1) if directed else n * (n - 1) // 2
    m = min(m, maxm); got = set(); tries = 0
    while len(got) < m and tries < 50 * (m + 1):
        tries += 1
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v or not ok(u, v): continue
        got.add((u, v) if directed else (min(u, v), max(u, v)))
    return list(got)


def _tree(rng, n, labels=None):
    p = labels or list(range(n))
    if labels is None: rng.shuffle(p)
    return [(p[i], p[rng.randrange(i)]) for i in range(1, n)]


def gen_und(rng, n, kind=None):
    cap = 3 * n
    kind = kind or rng.choice(["rand", "rand", "sparse", "tree", "forest", "cycle", "comps", "bip", "path", "star", "dense"])
    if n < 2: return []
    if kind == "rand": es = _rand_pairs(rng, n, rng.randrange(0, cap + 1), False)
    elif kind == "sparse": es = _rand_pairs(rng, n, rng.randrange(0, n // 2 + 2), False)
    elif kind == "dense": es = _rand_pairs(rng, n, cap, False)
    elif kind == "tree": es = _tree(rng, n)
    elif kind == "forest": es = [e for e in _tree(rng, n) if rng.random() < 0.75]
    elif kind == "cycle":
        p = list(range(n)); rng.shuffle(p)
        es = [(p[i], p[(i + 1) % n]) for i in range(n)] if n >= 3 else [(p[0], p[1])]
        es += _rand_pairs(rng, n, rng.randrange(0, 3), False)
    elif kind == "comps":
        p = list(range(n)); rng.shuffle(p); k = rng.randrange(1, min(n, 5) + 1)
        cuts = sorted(rng.sample(range(1, n), k - 1)) if k > 1 else []
        groups = [p[a:b] for a, b in zip([0] + cuts, cuts + [n])]; es = []
        for g in groups:
            es += _tree(rng, len(g), g) if len(g) > 1 else []
            if len(g) > 2:
                es += [(g[i], g[j]) for i, j in _rand_pairs(rng, len(g), rng.randrange(0, len(g)), False)]
    elif kind == "bip":
        side = [rng.randrange(2) for _ in range(n)]
        es = _rand_pairs(rng, n, rng.randrange(0, 2 * n + 1), False, lambda u, v: side[u] != side[v])
    elif kind == "path":
        p = list(range(n)); rng.shuffle(p); es = [(p[i], p[i + 1]) for i in range(n - 1)]
    else:  # star
        c = rng.randrange(n); es = [(c, v) for v in range(n) if v != c and rng.random() < 0.9]
    return _norm_und(rng, es)


def gen_dir(rng, n, kind=None):
    cap = 3 * n
    kind = kind or rng.choice(["rand", "rand", "sparse", "dag", "dag", "cycle", "comps", "dense", "path"])
    if n < 2: return []
    if kind == "rand": es = _rand_pairs(rng, n, rng.randrange(0, cap + 1), True)
    elif kind == "sparse": es = _rand_pairs(rng, n, rng.randrange(0, n + 2), True)
    elif kind == "dense": es = _rand_pairs(rng, n, cap, True)
    elif kind == "dag": es = gen_dag(rng, n)
    elif kind == "cycle":
        p = list(range(n)); rng.shuffle(p); k = rng.randrange(2, n + 1)
        es = [(p[i], p[(i + 1) % k]) for i in range(k)] + _rand_pairs(rng, n, rng.randrange(0, n + 1), True)
    elif kind == "comps":
        p = list(range(n)); rng.shuffle(p); h = rng.randrange(1, n)
        a, b = p[:h], p[h:]
        es = [(a[i], a[j]) for i, j in _rand_pairs(rng, len(a), rng.randrange(0, 2 * len(a) + 1), True)]
        es += [(b[i], b[j]) for i, j in _rand_pairs(rng, len(b), rng.randrange(0, 2 * len(b) + 1), True)]
    else:  # path, possibly reversed segments
        p = list(range(n)); rng.shuffle(p); es = [(p[i], p[i + 1]) for i in range(n - 1)]
    es = list(dict.fromkeys(es)); rng.shuffle(es)
    return es


def gen_dag(rng, n):
    if n < 2: return []
    p = list(range(n)); rng.shuffle(p); pos = {v: i for i, v in enumerate(p)}
    kind = rng.choice(["rand", "rand", "sparse", "dense", "chain", "tree"])
    if kind == "chain": es = [(p[i], p[i + 1]) for i in range(n - 1)] + _rand_pairs(rng, n, rng.randrange(0, n), True, lambda u, v: pos[u] < pos[v])
    elif kind == "tree": es = [(p[rng.randrange(i)], p[i]) for i in range(1, n)]
    else:
        m = {"rand": rng.randrange(0, 3 * n + 1), "sparse": rng.randrange(0, n + 1), "dense": 3 * n}[kind]
        es = _rand_pairs(rng, n, m, True, lambda u, v: pos[u] < pos[v])
    es = list(dict.fromkeys(es)); rng.shuffle(es)
    return es


# ---------------------------------------------------------------- hand-picked graphs
UG = [(0, []), (1, []), (2, []), (2, [(0, 1)]), (2, [(1, 0)]), (3, [(2, 1)]),
      (4, [(0, 1), (1, 2), (2, 3)]),                       # path
      (4, [(3, 2), (1, 2), (0, 1), (0, 3)]),               # 4-cycle, mixed orientation
      (3, [(0, 1), (1, 2), (0, 2)]),                       # triangle
      (5, [(1, 0), (2, 1), (3, 2), (4, 3), (4, 0)]),       # 5-cycle (odd)
      (5, [(0, 1), (0, 2), (0, 3), (0, 4)]),               # star
      (6, [(0, 1), (1, 2), (0, 2), (3, 4)]),               # triangle + edge + isolated vertex
      (7, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (5, 6)]),  # two triangles joined by a bridge
      (4, [(0, 1), (2, 3)])]                                # two disjoint edges
DG = [(0, []), (1, []), (2, []), (2, [(0, 1)]), (2, [(1, 0)]), (2, [(0, 1), (1, 0)]),
      (4, [(0, 1), (1, 2), (2, 3)]),                       # path
      (4, [(3, 2), (2, 1), (1, 0)]),                       # reversed path
      (3, [(0, 1), (1, 2), (2, 0)]),                       # 3-cycle
      (5, [(0, 1), (0, 2), (0, 3), (0, 4)]),               # out-star
      (5, [(1, 0), (2, 0), (3, 0), (4, 0)]),               # in-star
      (4, [(0, 1), (0, 2), (1, 3), (2, 3)]),               # diamond DAG
      (6, [(0, 1), (1, 0), (2, 3), (4, 5), (5, 3)]),       # disconnected
      (6, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)])]  # two cycles, one-way link
DAGS = [g for g in DG if is_dag(*g)] + [(6, [(5, 0), (4, 0), (3, 1), (5, 2), (2, 1), (0, 1)]),
                                         (5, [(4, 3), (3, 2), (2, 1), (1, 0), (4, 0)])]


def with_s(gs):
    out = []
    for n, es in gs:
        for s in sorted({0, n - 1, n // 2}):
            if n >= 1: out.append((n, s, es))
    return out


def with_st(gs):
    out = []
    for n, es in gs:
        if n >= 1:
            for s, t in sorted({(0, n - 1), (n - 1, 0), (0, 0), (n // 2, n - 1)}): out.append((n, s, t, es))
    return out


def P_und(x): return und_ok(x[0], x[-1])
def P_dir(x): return dir_ok(x[0], x[-1])
def P_und_s(x): return und_ok(x[0], x[-1]) and x[1] < x[0]
def P_dir_s(x): return dir_ok(x[0], x[-1]) and x[1] < x[0]
def P_und_st(x): return und_ok(x[0], x[-1]) and x[1] < x[0] and x[2] < x[0]
def P_dir_st(x): return dir_ok(x[0], x[-1]) and x[1] < x[0] and x[2] < x[0]
def P_dag(x): return is_dag(x[0], x[-1])


def g_und(r, n): return (n, gen_und(r, n))
def g_dir(r, n): return (n, gen_dir(r, n))
def g_und_s(r, n):
    n = max(n, 1); return (n, r.randrange(n), gen_und(r, n))
def g_dir_s(r, n):
    n = max(n, 1); return (n, r.randrange(n), gen_dir(r, n))


def _pick_t(r, n, s, reach):
    cand = [v for v in reach if v != s]
    if cand and r.random() < 0.7: return r.choice(cand)
    return r.randrange(n)


def g_und_st(r, n):
    n = max(n, 1); s = r.randrange(n); es = gen_und(r, n)
    d = bfs(uadj(n, es), s)
    return (n, s, _pick_t(r, n, s, [v for v in range(n) if d[v] != BIG]), es)


def _layers(r, n):
    """Random-labelled layered graph, complete between consecutive layers of width w: many equal-length paths."""
    w = r.choice([2, 3]); p = list(range(n)); r.shuffle(p)
    lay = [p[i:i + w] for i in range(0, n, w)]
    es = [(u, v) for a, b in zip(lay, lay[1:]) for u in a for v in b if r.random() < 0.9]
    r.shuffle(es)
    return es, lay


def g_dir_st(r, n):
    n = max(n, 1)
    if r.random() < 0.25:
        es, lay = _layers(r, n)
        return (n, r.choice(lay[0]), r.choice(lay[-1]), es)
    s = r.randrange(n); es = gen_dir(r, n, r.choice(["dense", "dense", "rand", "dag", "cycle"]))
    d = bfs(dadj(n, es), s)
    return (n, s, _pick_t(r, n, s, [v for v in range(n) if d[v] != BIG]), es)


# ================================================================ programs
# ---- reachability and traversal
def _reach_count(x):
    n, s, es = x
    return sum(1 for d in bfs(dadj(n, es), s) if d != BIG)
program("t3_reach_count", "T3",
        "Input is (n, s, edges) with s < n (so n >= 1). " + DIR +
        "Output the number of distinct vertices v such that there is a directed path (following edges forward) "
        "from s to v; s itself always counts (path of length 0), so the result is between 1 and n.",
        GS, u24, _reach_count, g_dir_s, S1, TS, edges=with_s(DG), pre=P_dir_s)


def _reach_queries(x):
    n, qs, es = x
    rs = reach_sets(n, es)
    return [1 if b in rs[a] else 0 for a, b in qs]
def _g_reach_queries(r, n):
    n = max(n, 1); es = gen_dir(r, n)
    return (n, [(r.randrange(n), r.randrange(n)) for _ in range(r.randrange(0, 2 * n + 2))], es)
program("t3_reach_queries", "T3",
        "Input is (n, queries, edges). " + DIR +
        "queries is a list of pairs (a, b) with a < n and b < n (repeats allowed; a may equal b). Output a list with "
        "one entry per query, in the same order as queries: 1 if there is a directed path (following edges forward, "
        "length 0 allowed) from a to b, else 0. In particular (a, a) gives 1. An empty query list gives [].",
        tup(u24, E, E), L, _reach_queries, _g_reach_queries, S1, TS,
        edges=[(1, [], []), (1, [(0, 0)], []), (2, [(0, 1), (1, 0), (1, 1)], [(0, 1)]),
               (3, [(0, 2), (2, 0), (1, 0)], [(0, 1), (1, 2)]), (3, [(2, 1), (1, 2)], [(0, 1), (1, 2), (2, 0)]),
               (6, [(0, 3), (2, 4), (4, 2), (5, 3), (3, 5)], [(0, 1), (1, 0), (2, 3), (4, 5), (5, 3)])],
        pre=lambda x: dir_ok(x[0], x[-1]) and all(a < x[0] and b < x[0] for a, b in x[1]))


def _bfs_order(x):
    n, s, es = x
    a = uadj(n, es); seen = [False] * n; seen[s] = True; q = deque([s]); out = []
    while q:
        u = q.popleft(); out.append(u)
        for v in a[u]:
            if not seen[v]: seen[v] = True; q.append(v)
    return out
program("t3_bfs_order", "T3",
        "Input is (n, s, edges) with s < n. " + UND +
        "Output the order in which breadth-first search from s visits vertices: start with a FIFO queue holding "
        "only s (s is marked seen); repeatedly remove the front vertex u, append u to the output, then scan the "
        "neighbours of u in INCREASING vertex-id order and append each not-yet-seen neighbour to the back of the "
        "queue, marking it seen. Stop when the queue is empty. The output starts with s and contains every vertex "
        "connected to s exactly once, and no other vertex.",
        GS, L, _bfs_order, g_und_s, S1, TS, edges=with_s(UG), pre=P_und_s)


# ---- distances
def _bfs_dist(x):
    n, s, es = x
    return bfs(dadj(n, es), s)
program("t3_bfs_dist", "T3",
        "Input is (n, s, edges) with s < n. " + DIR +
        "Output a list of length n whose entry v is the minimum number of edges on a directed path from s to v "
        "(following edges forward); entry s is 0, and entry v is 16777215 if v is not reachable from s.",
        GS, L, _bfs_dist, g_dir_s, S1, TS, edges=with_s(DG), pre=P_dir_s)


def _sp_len(x):
    n, s, t, es = x
    return bfs(uadj(n, es), s)[t]
program("t3_sp_len", "T3",
        "Input is (n, s, t, edges) with s < n and t < n. " + UND +
        "Output the length (number of edges) of a shortest path between s and t; 0 if s == t; 16777215 if s and t "
        "are in different connected components.",
        GST, u24, _sp_len, g_und_st, S1, TS, edges=with_st(UG), pre=P_und_st)


def _sp_count(x):
    n, s, t, es = x
    a = dadj(n, es); d = [BIG] * n; c = [0] * n; d[s] = 0; c[s] = 1; q = deque([s])
    while q:
        u = q.popleft()
        for v in a[u]:
            if d[v] == BIG: d[v] = d[u] + 1; c[v] = c[u]; q.append(v)
            elif d[v] == d[u] + 1: c[v] = (c[v] + c[u]) & M
    return c[t]
program("t3_sp_count", "T3",
        "Input is (n, s, t, edges) with s < n and t < n. " + DIR +
        "Let D be the minimum number of edges on a directed path from s to t. Output the number of distinct "
        "directed paths from s to t that have exactly D edges (two paths are distinct if their vertex sequences "
        "differ), reduced mod 2^24. If s == t the answer is 1 (the empty path). If t is not reachable from s the "
        "answer is 0.",
        GST, u24, _sp_count, g_dir_st, S1, TS,
        edges=with_st(DG) + [(6, 0, 5, [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4), (3, 5), (4, 5)])], pre=P_dir_st)


def _khop(x):
    n, s, k, es = x
    return sum(1 for d in bfs(uadj(n, es), s) if d <= k)
def _g_khop(r, n):
    n = max(n, 1)
    return (n, r.randrange(n), BIG if r.random() < 0.1 else r.randrange(0, 6), gen_und(r, n))
program("t3_khop", "T3",
        "Input is (n, s, k, edges) with s < n; k is any u24 value. " + UND +
        "Output the number of vertices v whose shortest-path distance (number of edges) from s is at most k. "
        "s itself always counts (distance 0); vertices not connected to s never count. k = 0 gives 1.",
        GST, u24, _khop, _g_khop, S1, TS,
        edges=[(n, s, k, es) for (n, s, es) in with_s(UG) for k in (0, 1, 2)] + [(4, 0, BIG, [(0, 1), (1, 2), (2, 3)])],
        pre=lambda x: und_ok(x[0], x[-1]) and x[1] < x[0])


# ---- connected components (undirected)
program("t3_cc_count", "T3",
        "Input is (n, edges). " + UND +
        "Output the number of connected components; every isolated vertex is a component of its own. n = 0 gives 0.",
        G, u24, lambda x: ncomps(uadj(*x)), g_und, S, TS, edges=UG, pre=P_und)

program("t3_cc_label", "T3",
        "Input is (n, edges). " + UND +
        "Output a list of length n whose entry v is the smallest vertex id in the connected component containing v "
        "(an isolated vertex is labelled with itself). n = 0 gives [].",
        G, L, lambda x: comps(uadj(*x)), g_und, S, TS, edges=UG, pre=P_und)


def _cc_largest(x):
    lab = comps(uadj(*x))
    return max((lab.count(v) for v in set(lab)), default=0)
program("t3_cc_largest", "T3",
        "Input is (n, edges). " + UND +
        "Output the number of vertices in the largest connected component (1 if there are no edges and n >= 1). "
        "n = 0 gives 0.",
        G, u24, _cc_largest, g_und, S, TS, edges=UG, pre=P_und)


# ---- bipartiteness and cycles (undirected)
def _two_colour(x):
    c = two_colour(*x)
    return c if c is not None else [BIG] * x[0]
program("t3_two_colour", "T3",
        "Input is (n, edges). " + UND +
        "If the graph is bipartite (has no cycle of odd length), output a list of length n with entries 0 or 1 "
        "such that the two endpoints of every edge get different values and, within each connected component, "
        "the smallest-numbered vertex gets 0 (this fixes the colouring uniquely; an isolated vertex gets 0). "
        "If the graph is not bipartite, output a list of n copies of 16777215. n = 0 gives [].",
        G, L, _two_colour, g_und, S, TS, edges=UG, pre=P_und)


def _bip_comps(x):
    n, es = x
    lab = comps(uadj(n, es))
    bad = set()
    for root in set(lab):
        vs = [v for v in range(n) if lab[v] == root]; idx = {v: i for i, v in enumerate(vs)}
        sub = [(idx[u], idx[v]) for u, v in es if lab[u] == root]
        if two_colour(len(vs), sub) is None: bad.add(root)
    return len(set(lab)) - len(bad)
program("t3_bipartite_comps", "T3",
        "Input is (n, edges). " + UND +
        "Output the number of connected components that are bipartite, i.e. contain no cycle of odd length "
        "(an isolated vertex is a bipartite component; a component containing a triangle is not). n = 0 gives 0.",
        G, u24, _bip_comps, g_und, S, TS, edges=UG, pre=P_und)


program("t3_cycle_rank", "T3",
        "Input is (n, edges). " + UND +
        "Output the cycle rank (circuit rank) m - n + c, where m is the number of edges and c the number of "
        "connected components (isolated vertices count as components). Equivalently, the number of edges that must "
        "be deleted to make the graph a forest. It is 0 exactly when the graph has no cycle.",
        G, u24, lambda x: len(x[1]) - x[0] + ncomps(uadj(*x)), g_und, S, TS, edges=UG, pre=P_und)


def _bridges(x):
    n, es = x; base = ncomps(uadj(n, es))
    return sum(1 for i in range(len(es)) if ncomps(uadj(n, es[:i] + es[i + 1:])) > base)
program("t3_bridges", "T3",
        "Input is (n, edges). " + UND +
        "Output the number of bridges: edges whose deletion (keeping all vertices) strictly increases the number "
        "of connected components. Every edge of a forest is a bridge; no edge on a cycle is a bridge.",
        G, u24, _bridges, g_und, S, TS, edges=UG, pre=P_und)


def _articulation(x):
    n, es = x; a = uadj(n, es); base = ncomps(a)
    return sum(1 for v in range(n) if ncomps(a, skip=v) > base)
program("t3_articulation", "T3",
        "Input is (n, edges). " + UND +
        "Output the number of articulation points: vertices v such that deleting v together with all its incident "
        "edges leaves a graph (on the other n-1 vertices) with strictly MORE connected components than the original "
        "graph. Isolated vertices and leaves (degree 1) are never articulation points; the centre of a star with at "
        "least 2 leaves is one.",
        G, u24, _articulation, g_und, S, TS, edges=UG, pre=P_und)


def _tree_parents(x):
    n, r, es = x
    a = uadj(n, es); p = [BIG] * n; seen = {r}; q = deque([r])
    while q:
        u = q.popleft()
        for v in a[u]:
            if v not in seen: seen.add(v); p[v] = u; q.append(v)
    return p
def _is_tree(n, es):
    return n >= 1 and und_ok(n, es) and len(es) == n - 1 and ncomps(uadj(n, es)) == 1
def _g_tree_parents(r, n):
    n = max(n, 1)
    kind = r.choice(["tree", "tree", "path", "star"])
    es = gen_und(r, n, kind)
    if kind == "star" and len(es) != n - 1: es = gen_und(r, n, "tree")
    return (n, r.randrange(n), es)
program("t3_tree_parents", "T3",
        "Input is (n, r, edges) with n >= 1 and r < n. " + UND +
        "Precondition: the edges form a tree spanning all n vertices (exactly n - 1 edges, connected). Root the tree "
        "at r and output a list of length n whose entry v is the parent of v, i.e. the neighbour of v on the unique "
        "path from v to r; entry r is 16777215.",
        GS, L, _tree_parents, _g_tree_parents, S1, TS,
        edges=[(1, 0, []), (2, 0, [(0, 1)]), (2, 1, [(0, 1)]), (4, 0, [(0, 1), (1, 2), (2, 3)]),
               (4, 3, [(0, 1), (1, 2), (2, 3)]), (4, 2, [(3, 2), (1, 2), (0, 1)]), (5, 0, [(0, 1), (0, 2), (0, 3), (0, 4)]),
               (5, 3, [(0, 1), (0, 2), (0, 3), (0, 4)]), (6, 4, [(5, 0), (0, 3), (3, 1), (3, 4), (2, 4)])],
        pre=lambda x: _is_tree(x[0], x[-1]) and x[1] < x[0])


# ---- directed structure
program("t3_scc_count", "T3",
        "Input is (n, edges). " + DIR +
        "Output the number of strongly connected components (u and v are in the same component iff each is "
        "reachable from the other by a directed path; every vertex is reachable from itself, so a vertex on no "
        "cycle is a component by itself). n = 0 gives 0.",
        G, u24, lambda x: len(set(scc_labels(*x))), g_dir, S, TS, edges=DG, pre=P_dir)

program("t3_scc_label", "T3",
        "Input is (n, edges). " + DIR +
        "Output a list of length n whose entry v is the smallest vertex id in the strongly connected component of "
        "v (the set of vertices u such that u is reachable from v and v is reachable from u by directed paths; it "
        "always contains v). n = 0 gives [].",
        G, L, lambda x: scc_labels(*x), g_dir, S, TS, edges=DG, pre=P_dir)


def _cyclic_vertices(x):
    lab = scc_labels(*x)
    return sum(1 for v in range(x[0]) if lab.count(lab[v]) >= 2)
program("t3_cyclic_vertices", "T3",
        "Input is (n, edges). " + DIR +
        "Output the number of vertices that lie on at least one directed cycle, i.e. vertices v with a directed "
        "path of length >= 1 from v back to v (equivalently, v's strongly connected component has at least 2 "
        "vertices). A DAG gives 0.",
        G, u24, _cyclic_vertices, g_dir, S, TS, edges=DG, pre=P_dir)


def _closure_size(x):
    return sum(len(r) - 1 for r in reach_sets(*x)) & M
program("t3_closure_size", "T3",
        "Input is (n, edges). " + DIR +
        "Output the number of ordered pairs (u, v) with u != v such that v is reachable from u by a directed path "
        "(the number of edges of the transitive closure), reduced mod 2^24.",
        G, u24, _closure_size, g_dir, S, TS, edges=DG, pre=P_dir)


program("t3_topo_order", "T3",
        "Input is (n, edges). " + DIR +
        "Precondition: the graph is acyclic (a DAG). Output the lexicographically smallest topological order: a "
        "list of all n vertices, each exactly once, in which u comes before v for every edge (u, v), and which among "
        "all such lists is smallest in lexicographic order. Equivalently: repeatedly output the smallest-numbered "
        "vertex not yet output all of whose in-neighbours have already been output. n = 0 gives [].",
        G, L, lambda x: _kahn(*x), lambda r, n: (n, gen_dag(r, n)), S, TS, edges=DAGS, pre=P_dag)


def _dag_longest(x):
    n, es = x
    a = dadj(n, es); best = [0] * n
    for u in reversed(_kahn(n, es)):
        best[u] = max((1 + best[v] for v in a[u]), default=0)
    return max(best, default=0)
program("t3_dag_longest", "T3",
        "Input is (n, edges). " + DIR +
        "Precondition: the graph is acyclic (a DAG). Output the maximum number of edges on any directed path. "
        "A graph with no edges (including n = 0 and n = 1) gives 0.",
        G, u24, _dag_longest, lambda r, n: (n, gen_dag(r, n)), S, TS, edges=DAGS, pre=P_dag)


# ---- degrees
def _degrees(x):
    n, es = x; d = [0] * n
    for u, v in es: d[u] += 1; d[v] += 1
    return d
program("t3_degrees", "T3",
        "Input is (n, edges). " + UND +
        "Output a list of length n whose entry v is the degree of v (the number of edges having v as an endpoint). "
        "n = 0 gives [].",
        G, L, _degrees, g_und, S, TS, edges=UG, pre=P_und)


def _in_out(x):
    n, es = x; i = [0] * n; o = [0] * n
    for u, v in es: o[u] += 1; i[v] += 1
    return (i, o)
program("t3_in_out_degrees", "T3",
        "Input is (n, edges). " + DIR +
        "Output a pair (ins, outs) of lists of length n: ins[v] is the number of edges (u, v) ending at v and "
        "outs[v] the number of edges (v, w) starting at v. n = 0 gives ([], []).",
        G, tup(L, L), _in_out, g_dir, S, TS, edges=DG, pre=P_dir)


def _sources_sinks(x):
    i, o = _in_out(x)
    return (sum(1 for d in i if d == 0), sum(1 for d in o if d == 0))
program("t3_sources_sinks", "T3",
        "Input is (n, edges). " + DIR +
        "Output a pair (sources, sinks): sources is the number of vertices with in-degree 0 (no edge ends at them) "
        "and sinks the number of vertices with out-degree 0 (no edge starts at them). An isolated vertex counts as "
        "both. n = 0 gives (0, 0).",
        G, tup(u24, u24), _sources_sinks, g_dir, S, TS, edges=DG, pre=P_dir)
