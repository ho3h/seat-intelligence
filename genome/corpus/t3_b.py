"""T3 Graph algorithms, part B (25 programs): weighted paths, spanning trees, structural and global measures.

Graph encoding (all programs): a graph is given by n = number of vertices (vertices are 0..n-1) and an edge list,
which is always the LAST element of the input tuple; any extra scalars (source, target, k, ...) come between n and
the edge list. An unweighted edge is (u, v); a weighted edge is (u, v, w) with 1 <= w <= 1000.
Undirected graphs list each edge once in either orientation; directed edges (u, v) mean u -> v.
There are never self loops, never duplicate or parallel edges (in an undirected graph (u, v) and (v, u) are the
same edge and never both appear; in a directed graph (u, v) and (v, u) may both appear). Edge order is arbitrary.
16777215 (= 2^24 - 1) is used as "infinity / none"."""
from collections import deque
from . import program
from ..types import u24, list_of, tup, MASK

M = MASK
INF = MASK  # 16777215
L = list_of(u24)
E2 = list_of(tup(u24, u24))
E3 = list_of(tup(u24, u24, u24))
S = list(range(0, 9))           # authoring sizes (vertex counts)
T = [64, 128]                   # test sizes
S_SMALL = list(range(0, 6))     # for cubic / quadratic-output programs
T_SMALL = [40, 80]

UND = "Undirected"
DIR = "Directed"


# ---------------------------------------------------------------- validation (preconditions)
def _ok_edges(n, edges, weighted, directed):
    if not isinstance(n, int) or n < 0: return False
    seen = set()
    for e in edges:
        if len(e) != (3 if weighted else 2): return False
        u, v = e[0], e[1]
        if not (0 <= u < n and 0 <= v < n) or u == v: return False
        if weighted and not (1 <= e[2] <= 1000): return False
        key = (u, v) if directed else (min(u, v), max(u, v))
        if key in seen: return False
        seen.add(key)
    return True


def und_ok(weighted):
    return lambda x: _ok_edges(x[0], x[-1], weighted, False)


def dir_ok(weighted):
    return lambda x: _ok_edges(x[0], x[-1], weighted, True)


def _adj(n, edges, directed=False):
    adj = [[] for _ in range(n)]
    for e in edges:
        u, v = e[0], e[1]
        w = e[2] if len(e) > 2 else 1
        adj[u].append((v, w))
        if not directed: adj[v].append((u, w))
    return adj


def _comps(n, edges, removed=None):
    """Number of connected components of the undirected graph, ignoring vertex `removed`."""
    p = list(range(n))
    def f(a):
        while p[a] != a:
            p[a] = p[p[a]]; a = p[a]
        return a
    for e in edges:
        u, v = e[0], e[1]
        if u == removed or v == removed: continue
        a, b = f(u), f(v)
        if a != b: p[a] = b
    return sum(1 for i in range(n) if i != removed and f(i) == i)


def connected(x):
    n = x[0]
    return n <= 1 or _comps(n, x[-1]) == 1


def is_forest(x):
    n, edges = x[0], x[-1]
    return len(edges) == n - _comps(n, edges)


def both(*fs):
    return lambda x: all(f(x) for f in fs)


# ---------------------------------------------------------------- generators
def _w(rng, small):
    return rng.randint(1, 5) if small else rng.randint(1, 1000)


def _orient(rng, u, v):
    return (u, v) if rng.random() < 0.5 else (v, u)


def rand_und(rng, n, m=None, weighted=False, small_w=None):
    """Random simple undirected graph with about m edges (default: up to ~3n, denser when n is small)."""
    pairs = n * (n - 1) // 2
    if m is None: m = rng.randint(0, min(pairs, max(3 * n, 0)))
    m = min(m, pairs)
    if small_w is None: small_w = rng.random() < 0.4
    chosen = set()
    if pairs and m > pairs // 2:  # dense: sample from all pairs
        allp = [(u, v) for u in range(n) for v in range(u + 1, n)]
        chosen = set(rng.sample(allp, m))
    else:
        while len(chosen) < m:
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v: chosen.add((min(u, v), max(u, v)))
    out = []
    for u, v in chosen:
        a, b = _orient(rng, u, v)
        out.append((a, b, _w(rng, small_w)) if weighted else (a, b))
    rng.shuffle(out)
    return out


def rand_connected(rng, n, extra=None, weighted=False, small_w=None):
    """Random connected simple undirected graph: random spanning tree plus `extra` more edges."""
    if small_w is None: small_w = rng.random() < 0.4
    perm = list(range(n)); rng.shuffle(perm)
    chosen = set()
    for i in range(1, n):
        u, v = perm[i], perm[rng.randrange(i)]
        chosen.add((min(u, v), max(u, v)))
    pairs = n * (n - 1) // 2
    if extra is None: extra = rng.randint(0, min(pairs - len(chosen), 2 * n)) if n > 1 else 0
    target = min(pairs, len(chosen) + extra)
    while len(chosen) < target:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v: chosen.add((min(u, v), max(u, v)))
    out = []
    for u, v in chosen:
        a, b = _orient(rng, u, v)
        out.append((a, b, _w(rng, small_w)) if weighted else (a, b))
    rng.shuffle(out)
    return out


def rand_forest(rng, n):
    p_attach = rng.choice([0.5, 0.8, 1.0])
    perm = list(range(n)); rng.shuffle(perm)
    out = []
    for i in range(1, n):
        if rng.random() < p_attach:
            out.append(_orient(rng, perm[i], perm[rng.randrange(i)]))
    rng.shuffle(out)
    return out


def rand_dir(rng, n, m=None, weighted=False, small_w=None):
    pairs = n * (n - 1)
    if m is None: m = rng.randint(0, min(pairs, 3 * n))
    m = min(m, pairs)
    if small_w is None: small_w = rng.random() < 0.4
    chosen = set()
    if pairs and m > pairs // 2:
        allp = [(u, v) for u in range(n) for v in range(n) if u != v]
        chosen = set(rng.sample(allp, m))
    else:
        while len(chosen) < m:
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v: chosen.add((u, v))
    out = [(u, v, _w(rng, small_w)) if weighted else (u, v) for u, v in chosen]
    rng.shuffle(out)
    return out


def vtx(rng, n):
    """A vertex id, usually in range, occasionally out of range (n or n+1)."""
    return rng.randrange(n) if n and rng.random() < 0.9 else n + rng.randrange(2)


# ================================================================ 1. s-t shortest path (weighted, undirected)
def _dijkstra(n, s, adj):
    dist = [INF] * n
    if s >= n: return dist
    import heapq
    dist[s] = 0; h = [(0, s)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]: continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w; heapq.heappush(h, (d + w, v))
    return dist


def _st_dist(x):
    n, s, t, edges = x
    if s >= n or t >= n: return INF
    return _dijkstra(n, s, _adj(n, edges))[t]


program("t3_wsp_dist", "T3",
        f"{UND} weighted graph. Input is (n, s, t, edges) with edges (u, v, w). Output the minimum total weight of a "
        "path from s to t (sum of its edge weights). s == t (with s < n) gives 0. If t is unreachable from s, or s >= n, "
        "or t >= n, output 16777215. (Path sums never reach 2^24 for the sizes used.)",
        tup(u24, u24, u24, E3), u24, _st_dist,
        lambda r, n: (n, vtx(r, n), vtx(r, n), rand_und(r, n, weighted=True)), S, T,
        edges=[(0, 0, 0, []), (1, 0, 0, []), (2, 0, 1, []), (2, 0, 1, [(1, 0, 7)]),
               (3, 0, 2, [(0, 1, 1), (1, 2, 1), (0, 2, 5)]), (3, 0, 2, [(0, 1, 4), (1, 2, 4), (2, 0, 5)]),
               (3, 0, 5, [(0, 1, 1)]), (4, 3, 0, [(0, 1, 1000), (1, 2, 1000), (2, 3, 1000)])],
        pre=und_ok(True))


# ================================================================ 2. single-source distances (weighted, directed)
def _sssp(x):
    n, s, edges = x
    return _dijkstra(n, s, _adj(n, edges, directed=True))


program("t3_wsp_all_from", "T3",
        f"{DIR} weighted graph. Input is (n, s, edges) with edges (u, v, w) meaning an arc u -> v of weight w. Output a "
        "list of length n whose entry v is the minimum total weight of a directed path from s to v; entry s is 0; "
        "vertices not reachable from s get 16777215. If s >= n every entry is 16777215 (the list still has length n).",
        tup(u24, u24, E3), L, _sssp,
        lambda r, n: (n, vtx(r, n), rand_dir(r, n, weighted=True)), S, T,
        edges=[(0, 0, []), (1, 0, []), (2, 0, [(1, 0, 3)]), (2, 1, [(1, 0, 3)]), (2, 2, [(0, 1, 1)]),
               (4, 0, [(0, 1, 5), (1, 2, 5), (0, 2, 20), (2, 3, 1), (3, 0, 1)]),
               (3, 0, [(0, 1, 2), (1, 0, 9), (0, 2, 1)])],
        pre=dir_ok(True))


# ================================================================ 3. minimum spanning forest weight
def _kruskal(n, edges, skip=None):
    """-> (total weight, list of chosen edge indices). Edges considered by (w, index)."""
    p = list(range(n))
    def f(a):
        while p[a] != a:
            p[a] = p[p[a]]; a = p[a]
        return a
    tot, used = 0, []
    for i in sorted(range(len(edges)), key=lambda i: (edges[i][2], i)):
        if i == skip: continue
        u, v, w = edges[i]
        a, b = f(u), f(v)
        if a != b: p[a] = b; tot += w; used.append(i)
    return tot, used


program("t3_msf_weight", "T3",
        f"{UND} weighted graph, not necessarily connected. Input is (n, edges) with edges (u, v, w). Output the total "
        "weight of a minimum spanning forest: the sum, over all connected components, of the weight of a minimum "
        "spanning tree of that component (isolated vertices contribute 0), mod 2^24. No edges gives 0.",
        tup(u24, E3), u24, lambda x: _kruskal(x[0], x[1])[0] & M,
        lambda r, n: (n, rand_und(r, n, weighted=True)), S, T,
        edges=[(0, []), (1, []), (2, [(0, 1, 9)]), (3, [(0, 1, 1), (1, 2, 2), (0, 2, 3)]),
               (4, [(0, 1, 5), (2, 3, 7)]), (4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)])],
        pre=und_ok(True))


# ================================================================ 4. second-best spanning tree weight
def _mst2(x):
    n, edges = x
    if n <= 1: return INF
    _, used = _kruskal(n, edges)
    best = INF
    for i in used:
        w, u2 = _kruskal(n, edges, skip=i)
        if len(u2) == n - 1: best = min(best, w)
    return best


program("t3_mst_second", "T3",
        f"{UND} weighted CONNECTED graph (precondition). Input is (n, edges) with edges (u, v, w). Consider every spanning "
        "tree (every set of n-1 edges connecting all n vertices; two trees are different if their edge sets differ) and "
        "list their total weights in ascending order, keeping repeats. Output the SECOND entry of that list: so if two "
        "different spanning trees both have the minimum weight, the answer equals the minimum weight. If there are "
        "fewer than two spanning trees (the graph is itself a tree, including n <= 1), output 16777215.",
        tup(u24, E3), u24, _mst2,
        lambda r, n: (n, rand_connected(r, n, extra=None if r.random() < 0.8 else 0, weighted=True)), S, T,
        edges=[(0, []), (1, []), (2, [(0, 1, 4)]), (3, [(0, 1, 1), (1, 2, 2), (2, 0, 3)]),
               (3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)]), (4, [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 0, 10), (0, 2, 4)])],
        pre=both(und_ok(True), connected))


# ================================================================ 5. all-pairs shortest paths (weighted, directed)
def _apsp(x):
    n, edges = x
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges: d[u][v] = min(d[u][v], w)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF: continue
            di = d[i]
            for j in range(n):
                if dk[j] != INF and dik + dk[j] < di[j]: di[j] = dik + dk[j]
    return d


program("t3_apsp_matrix", "T3",
        f"{DIR} weighted graph. Input is (n, edges) with edges (u, v, w) meaning an arc u -> v of weight w. Output the "
        "n x n distance matrix as a list of n rows, row i being a list of n entries: entry j of row i is the minimum "
        "total weight of a directed path from i to j, 0 when i == j, and 16777215 when j is not reachable from i. "
        "n = 0 gives the empty list.",
        tup(u24, E3), list_of(L), _apsp,
        lambda r, n: (n, rand_dir(r, n, weighted=True)), S_SMALL, T_SMALL,
        edges=[(0, []), (1, []), (2, [(0, 1, 5)]), (2, [(0, 1, 5), (1, 0, 2)]),
               (3, [(0, 1, 1), (1, 2, 1), (0, 2, 5), (2, 0, 1)])],
        pre=dir_ok(True))


# ================================================================ 6. eccentricities (unweighted, connected)
def _bfs(n, adj, s):
    d = [INF] * n; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if d[v] == INF: d[v] = d[u] + 1; q.append(v)
    return d


def _ecc(x):
    n, edges = x
    adj = _adj(n, edges)
    return [max(_bfs(n, adj, s)) for s in range(n)]


program("t3_eccentricities", "T3",
        f"{UND} unweighted CONNECTED graph (precondition). Input is (n, edges) with edges (u, v). Output a list of length "
        "n whose entry v is the eccentricity of v: the largest number of edges on a shortest path from v to any other "
        "vertex (the maximum over all u of the hop distance between v and u). A single vertex has eccentricity 0; "
        "n = 0 gives the empty list.",
        tup(u24, E2), L, _ecc,
        lambda r, n: (n, rand_connected(r, n, extra=r.randint(0, n))), S, T,
        edges=[(0, []), (1, []), (2, [(1, 0)]), (3, [(0, 1), (1, 2)]), (3, [(0, 1), (1, 2), (2, 0)]),
               (5, [(0, 1), (1, 2), (2, 3), (3, 4)]), (4, [(0, 1), (0, 2), (0, 3)])],
        pre=both(und_ok(False), connected))


# ================================================================ 7. Wiener index
def _wiener(x):
    n, edges = x
    adj = _adj(n, edges)
    return sum(sum(_bfs(n, adj, s)[s + 1:]) for s in range(n)) & M


program("t3_wiener_index", "T3",
        f"{UND} unweighted CONNECTED graph (precondition). Input is (n, edges) with edges (u, v). Output the sum, over all "
        "unordered pairs of distinct vertices {u, v}, of the hop distance (number of edges on a shortest path) between "
        "u and v, mod 2^24. n <= 1 gives 0.",
        tup(u24, E2), u24, _wiener,
        lambda r, n: (n, rand_connected(r, n, extra=r.randint(0, n))), S, T,
        edges=[(0, []), (1, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2)]), (3, [(0, 1), (1, 2), (0, 2)]),
               (4, [(0, 1), (0, 2), (0, 3)]), (4, [(0, 1), (1, 2), (2, 3)])],
        pre=both(und_ok(False), connected))


# ================================================================ 8. triangle count
def _triangles(x):
    n, edges = x
    nb = [set() for _ in range(n)]
    for u, v in edges: nb[u].add(v); nb[v].add(u)
    c = 0
    for u, v in edges:
        c += sum(1 for w in nb[u] & nb[v])
    return (c // 3) & M


def _gen_tri(r, n):
    return (n, rand_und(r, n, m=r.randint(0, n * (n - 1) // 2) if n <= 8 else None))


program("t3_triangle_count", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Output the number of triangles: unordered sets "
        "of three distinct vertices {a, b, c} such that all three edges a-b, b-c, a-c are present, mod 2^24.",
        tup(u24, E2), u24, _triangles, _gen_tri, S, T,
        edges=[(0, []), (3, [(0, 1), (1, 2)]), (3, [(0, 1), (1, 2), (2, 0)]),
               (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]), (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])],
        pre=und_ok(False))


# ================================================================ 9. max-degree vertex
def _maxdeg(x):
    n, edges = x
    if n == 0: return INF
    deg = [0] * n
    for u, v in edges: deg[u] += 1; deg[v] += 1
    best = max(deg)
    return deg.index(best)


program("t3_max_degree_vertex", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). The degree of a vertex is the number of edges "
        "touching it. Output the vertex of largest degree; on ties output the smallest such vertex id (so a graph with "
        "no edges and n >= 1 gives 0). n = 0 gives 16777215.",
        tup(u24, E2), u24, _maxdeg, lambda r, n: (n, rand_und(r, n)), S, T,
        edges=[(0, []), (1, []), (3, []), (3, [(2, 1)]), (4, [(3, 0), (3, 1), (0, 1)]), (4, [(0, 1), (2, 3)])],
        pre=und_ok(False))


# ================================================================ 10. bipartite maximum matching
def _matching(x):
    a, b, edges = x
    adj = [[] for _ in range(a)]
    for u, v in edges: adj[u].append(v)
    for l in adj: l.sort()
    match_r = [-1] * b

    def aug(u, seen):
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                if match_r[v] < 0 or aug(match_r[v], seen):
                    match_r[v] = u; return True
        return False
    return sum(1 for u in range(a) if aug(u, [False] * b))


def _gen_match(r, n):
    a = r.randint(0, n); b = r.randint(0, n)
    pairs = a * b
    m = r.randint(0, min(pairs, 3 * n))
    chosen = set()
    if pairs and m > pairs // 2:
        chosen = set(r.sample([(u, v) for u in range(a) for v in range(b)], m))
    else:
        while len(chosen) < m: chosen.add((r.randrange(a), r.randrange(b)))
    out = list(chosen); r.shuffle(out)
    return (a, b, out)


def _match_ok(x):
    a, b, edges = x
    return (all(0 <= u < a and 0 <= v < b for u, v in edges) and len(set(edges)) == len(edges))


program("t3_bipartite_matching", "T3",
        "Bipartite graph given by its two sides. Input is (a, b, edges): the left side has vertices 0..a-1, the right "
        "side has vertices 0..b-1 (a separate numbering), and each edge (u, v) joins left vertex u (u < a) to right "
        "vertex v (v < b); no pair appears twice. Output the size of a maximum matching: the largest number of edges "
        "that can be chosen so that no two chosen edges share a left vertex or share a right vertex.",
        tup(u24, u24, E2), u24, _matching, _gen_match, S, T,
        edges=[(0, 0, []), (3, 0, []), (1, 1, [(0, 0)]), (2, 2, [(0, 0), (1, 0)]),
               (2, 2, [(0, 0), (0, 1), (1, 0)]), (3, 3, [(0, 0), (0, 1), (1, 0), (2, 2), (1, 2)])],
        pre=_match_ok)


# ================================================================ 11. greedy colouring
def _greedy(x):
    n, edges = x
    nb = [[] for _ in range(n)]
    for u, v in edges: nb[u].append(v); nb[v].append(u)
    col = []
    for v in range(n):
        used = {col[u] for u in nb[v] if u < v}
        c = 0
        while c in used: c += 1
        col.append(c)
    return col


program("t3_greedy_coloring", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Colour the vertices greedily in increasing id "
        "order 0, 1, ..., n-1: vertex v receives the smallest colour c >= 0 that differs from the colours already given "
        "to all neighbours of v with smaller id. Output the list of the n colours, entry v being the colour of vertex v.",
        tup(u24, E2), L, _greedy, lambda r, n: (n, rand_und(r, n)), S, T,
        edges=[(0, []), (2, []), (2, [(1, 0)]), (3, [(0, 1), (1, 2), (0, 2)]), (4, [(0, 3), (1, 2)]),
               (4, [(0, 2), (1, 3), (2, 3)])],
        pre=und_ok(False))


# ================================================================ 12. clique number
def _clique(x):
    n, edges = x
    if n == 0: return 0
    nb = [set() for _ in range(n)]
    for u, v in edges: nb[u].add(v); nb[v].add(u)
    best = 0

    def bk(size, P, X):
        nonlocal best
        if not P and not X:
            best = max(best, size); return
        if size + len(P) <= best: return
        piv = max(P | X, key=lambda u: len(nb[u] & P))
        for v in list(P - nb[piv]):
            bk(size + 1, P & nb[v], X & nb[v])
            P = P - {v}; X = X | {v}
    bk(0, set(range(n)), set())
    return best


def _gen_clique(r, n):
    if n <= 8:
        return (n, rand_und(r, n, m=r.randint(0, n * (n - 1) // 2)))
    es = rand_und(r, n)
    if r.random() < 0.6:  # plant a clique
        k = r.randint(3, 7)
        vs = r.sample(range(n), k)
        have = {(min(e), max(e)) for e in es}
        for i in range(k):
            for j in range(i + 1, k):
                a, b = min(vs[i], vs[j]), max(vs[i], vs[j])
                if (a, b) not in have: have.add((a, b)); es.append(_orient(r, a, b))
        r.shuffle(es)
    return (n, es)


program("t3_clique_number", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Output the size of the largest clique: the "
        "largest number of vertices that are pairwise adjacent. Any single vertex is a clique of size 1, so n >= 1 "
        "with no edges gives 1; n = 0 gives 0.",
        tup(u24, E2), u24, _clique, _gen_clique, S, T,
        edges=[(0, []), (1, []), (3, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2), (2, 0)]),
               (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]), (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])],
        pre=und_ok(False))


# ================================================================ 13. maximum independent set of a forest
def _forest_mis(x):
    n, edges = x
    adj = _adj(n, edges)
    seen = [False] * n; total = 0
    for root in range(n):
        if seen[root]: continue
        order, parent = [], {root: -1}
        seen[root] = True; st = [root]
        while st:
            u = st.pop(); order.append(u)
            for v, _ in adj[u]:
                if not seen[v]: seen[v] = True; parent[v] = u; st.append(v)
        inc, exc = {}, {}
        for u in reversed(order):
            kids = [v for v, _ in adj[u] if parent.get(v) == u and v != parent[u]]
            inc[u] = 1 + sum(exc[v] for v in kids)
            exc[u] = sum(max(inc[v], exc[v]) for v in kids)
        total += max(inc[root], exc[root])
    return total


program("t3_forest_mis", "T3",
        f"{UND} unweighted graph that is a FOREST (precondition: no cycles; it may be disconnected). Input is (n, edges) "
        "with edges (u, v). Output the size of a maximum independent set: the largest number of vertices no two of "
        "which are joined by an edge. Isolated vertices always count; n = 0 gives 0.",
        tup(u24, E2), u24, _forest_mis, lambda r, n: (n, rand_forest(r, n)), S, T,
        edges=[(0, []), (1, []), (3, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2)]), (4, [(0, 1), (0, 2), (0, 3)]),
               (5, [(0, 1), (1, 2), (2, 3), (3, 4)]), (4, [(0, 1), (2, 3)])],
        pre=both(und_ok(False), is_forest))


# ================================================================ 14. line-graph edge count
def _line_edges(x):
    n, edges = x
    deg = [0] * n
    for u, v in edges: deg[u] += 1; deg[v] += 1
    return sum(d * (d - 1) // 2 for d in deg) & M


program("t3_line_graph_edges", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Output the number of edges of its line graph, "
        "i.e. the number of unordered pairs of distinct edges that share an endpoint (equivalently the sum over all "
        "vertices of deg*(deg-1)/2, deg = number of edges touching the vertex), mod 2^24.",
        tup(u24, E2), u24, _line_edges, lambda r, n: (n, rand_und(r, n)), S, T,
        edges=[(0, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2)]), (3, [(0, 1), (1, 2), (2, 0)]),
               (4, [(0, 1), (0, 2), (0, 3)]), (4, [(0, 1), (2, 3)])],
        pre=und_ok(False))


# ================================================================ 15. number of walks of length k
def _walks(x):
    n, s, t, k, edges = x
    if s >= n or t >= n: return 0
    cnt = [0] * n; cnt[s] = 1
    for _ in range(k):
        nxt = [0] * n
        for u, v in edges:
            if cnt[u]: nxt[v] = (nxt[v] + cnt[u]) & M
        cnt = nxt
    return cnt[t]


def _gen_walks(r, n):
    m = r.randint(0, min(n * (n - 1), 3 * n)) if n > 8 else None
    return (n, vtx(r, n), vtx(r, n), r.randint(0, n + 2), rand_dir(r, n, m=m))


program("t3_walk_count", "T3",
        f"{DIR} unweighted graph. Input is (n, s, t, k, edges) with edges (u, v) meaning an arc u -> v. Output the number "
        "of walks from s to t that use exactly k arcs, mod 2^24. A walk is a sequence of vertices s = x0, x1, ..., xk = t "
        "with every xi -> x(i+1) an arc; vertices and arcs may repeat. k = 0 gives 1 if s == t and 0 otherwise. If "
        "s >= n or t >= n output 0.",
        tup(u24, u24, u24, u24, E2), u24, _walks, _gen_walks, S, T,
        edges=[(0, 0, 0, 0, []), (1, 0, 0, 0, []), (1, 0, 0, 3, []), (2, 0, 1, 1, [(0, 1)]), (2, 1, 0, 1, [(0, 1)]),
               (2, 0, 0, 4, [(0, 1), (1, 0)]), (3, 0, 2, 2, [(0, 1), (1, 2), (0, 2)]),
               (3, 0, 0, 30, [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]), (2, 2, 0, 0, [(0, 1)])],
        pre=dir_ok(False))


# ================================================================ 16. reachable within a weight budget
def _budget(x):
    n, s, b, edges = x
    if s >= n: return 0
    return sum(1 for d in _dijkstra(n, s, _adj(n, edges)) if d <= b)


program("t3_budget_reach", "T3",
        f"{UND} weighted graph. Input is (n, s, b, edges) with edges (u, v, w). Output the number of vertices v whose "
        "shortest-path distance from s (minimum total edge weight of a path from s to v) is at most b. s itself has "
        "distance 0 and always counts; unreachable vertices never count. If s >= n output 0.",
        tup(u24, u24, u24, E3), u24, _budget,
        lambda r, n: (n, vtx(r, n), r.choice([0, r.randint(0, 20), r.randint(0, 3000)]), rand_und(r, n, weighted=True)),
        S, T,
        edges=[(0, 0, 5, []), (1, 0, 0, []), (3, 0, 0, [(0, 1, 1)]), (3, 0, 1, [(0, 1, 1), (1, 2, 1)]),
               (3, 0, 2, [(0, 1, 1), (1, 2, 1)]), (3, 3, 100, [(0, 1, 1)]), (3, 2, 5, [(0, 1, 1), (1, 2, 5), (0, 2, 9)])],
        pre=und_ok(True))


# ================================================================ 17. minimax (bottleneck) path
def _minimax(x):
    n, s, t, edges = x
    if s >= n or t >= n: return INF
    if s == t: return 0
    p = list(range(n))
    def f(a):
        while p[a] != a:
            p[a] = p[p[a]]; a = p[a]
        return a
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        p[f(u)] = f(v)
        if f(s) == f(t): return w
    return INF


program("t3_minimax_path", "T3",
        f"{UND} weighted graph. Input is (n, s, t, edges) with edges (u, v, w). The bottleneck of a path is the largest "
        "edge weight on it. Output the minimum bottleneck over all paths from s to t. s == t (with s < n) gives 0. If t "
        "is unreachable from s, or s >= n, or t >= n, output 16777215.",
        tup(u24, u24, u24, E3), u24, _minimax,
        lambda r, n: (n, vtx(r, n), vtx(r, n), rand_und(r, n, weighted=True)), S, T,
        edges=[(0, 0, 0, []), (1, 0, 0, []), (2, 0, 1, []), (2, 1, 0, [(0, 1, 7)]),
               (3, 0, 2, [(0, 1, 5), (1, 2, 6), (0, 2, 9)]), (3, 0, 2, [(0, 1, 5), (1, 2, 10), (0, 2, 9)]),
               (3, 0, 7, [(0, 1, 1)])],
        pre=und_ok(True))


# ================================================================ 18. cheapest walk with exactly k arcs
def _kwalk(x):
    n, s, t, k, edges = x
    if s >= n or t >= n: return INF
    d = [INF] * n; d[s] = 0
    for _ in range(k):
        nd = [INF] * n
        for u, v, w in edges:
            if d[u] != INF and d[u] + w < nd[v]: nd[v] = d[u] + w
        d = nd
    return d[t]


def _gen_kwalk(r, n):
    m = r.randint(n, min(n * (n - 1), 3 * n)) if n > 8 else None
    return (n, vtx(r, n), vtx(r, n), r.randint(0, n + 2), rand_dir(r, n, m=m, weighted=True))


program("t3_cheapest_k_walk", "T3",
        f"{DIR} weighted graph. Input is (n, s, t, k, edges) with edges (u, v, w) meaning an arc u -> v of weight w. "
        "Output the minimum total weight of a walk from s to t that uses exactly k arcs (vertices and arcs may repeat; "
        "a repeated arc counts its weight each time). k = 0 gives 0 if s == t and 16777215 otherwise. If no such walk "
        "exists, or s >= n, or t >= n, output 16777215.",
        tup(u24, u24, u24, u24, E3), u24, _kwalk, _gen_kwalk, S, T,
        edges=[(0, 0, 0, 0, []), (1, 0, 0, 0, []), (1, 0, 0, 1, []), (2, 0, 1, 1, [(0, 1, 4)]),
               (2, 0, 1, 3, [(0, 1, 4), (1, 0, 1)]), (2, 0, 1, 2, [(0, 1, 4), (1, 0, 1)]),
               (3, 0, 2, 2, [(0, 1, 1), (1, 2, 1), (0, 2, 1), (2, 1, 5)]), (2, 3, 0, 0, [(0, 1, 1)])],
        pre=dir_ok(True))


# ================================================================ 19. girth
def _girth(x):
    n, edges = x
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges): adj[u].append((v, i)); adj[v].append((u, i))
    best = INF
    for i, (s, t) in enumerate(edges):
        d = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            if u == t: break
            for v, j in adj[u]:
                if j != i and v not in d: d[v] = d[u] + 1; q.append(v)
        if t in d: best = min(best, d[t] + 1)
    return 0 if best == INF else best


def _gen_girth(r, n):
    if r.random() < 0.5:  # sparse: a forest plus a few edges, to get long shortest cycles
        es = rand_forest(r, n)
        have = {(min(e), max(e)) for e in es}
        for _ in range(r.randint(0, 2)):
            if n < 2: break
            u, v = r.sample(range(n), 2)
            if (min(u, v), max(u, v)) not in have: have.add((min(u, v), max(u, v))); es.append((u, v))
        return (n, es)
    return (n, rand_und(r, n))


program("t3_girth", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Output the girth: the number of edges of the "
        "shortest cycle (a closed path of at least 3 distinct vertices, no vertex repeated except start = end). If the "
        "graph has no cycle (it is a forest) output 0.",
        tup(u24, E2), u24, _girth, _gen_girth, S, T,
        edges=[(0, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2), (2, 0)]), (4, [(0, 1), (1, 2), (2, 3), (3, 0)]),
               (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]), (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]),
               (4, [(0, 1), (0, 2), (0, 3)])],
        pre=und_ok(False))


# ================================================================ 20. articulation points
def _artic(x):
    n, edges = x
    c = _comps(n, edges)
    return [v for v in range(n) if _comps(n, edges, removed=v) > c]


program("t3_articulation_points", "T3",
        f"{UND} unweighted graph, not necessarily connected. Input is (n, edges) with edges (u, v). A vertex is a cut "
        "vertex if deleting it (together with its edges) leaves strictly more connected components among the remaining "
        "n-1 vertices than the whole graph had (isolated vertices and leaves are never cut vertices). Output the list "
        "of all cut vertices in ascending order (empty if none).",
        tup(u24, E2), L, _artic, lambda r, n: (n, rand_und(r, n, m=r.randint(0, 2 * n))), S, T,
        edges=[(0, []), (1, []), (2, [(0, 1)]), (3, [(0, 1), (1, 2)]), (3, [(0, 1), (1, 2), (2, 0)]),
               (5, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4)]), (6, [(0, 1), (1, 2), (3, 4), (4, 5)])],
        pre=und_ok(False))


# ================================================================ 21. Euler trail start
def _euler(x):
    n, edges = x
    if not edges: return INF
    deg = [0] * n
    for u, v in edges: deg[u] += 1; deg[v] += 1
    p = list(range(n))
    def f(a):
        while p[a] != a:
            p[a] = p[p[a]]; a = p[a]
        return a
    for u, v in edges: p[f(u)] = f(v)
    roots = {f(v) for v in range(n) if deg[v]}
    if len(roots) != 1: return INF
    odd = [v for v in range(n) if deg[v] % 2]
    if not odd: return min(v for v in range(n) if deg[v])
    if len(odd) == 2: return odd[0]
    return INF


def _gen_euler(r, n):
    es = rand_connected(r, n, extra=r.randint(0, n)) if r.random() < 0.7 else rand_und(r, n)
    if n >= 2 and r.random() < 0.75:  # repair parities by toggling edges between odd vertices
        have = {(min(u, v), max(u, v)) for u, v in es}
        deg = [0] * n
        for u, v in es: deg[u] += 1; deg[v] += 1
        odd = [v for v in range(n) if deg[v] % 2]; r.shuffle(odd)
        keep = 2 if r.random() < 0.4 else 0
        for i in range(0, len(odd) - keep, 2):
            a, b = min(odd[i], odd[i + 1]), max(odd[i], odd[i + 1])
            if (a, b) in have: have.remove((a, b))
            else: have.add((a, b))
        es = [_orient(r, a, b) for a, b in have]; r.shuffle(es)
    return (n, es)


program("t3_euler_start", "T3",
        f"{UND} unweighted graph. Input is (n, edges) with edges (u, v). Decide whether some walk uses every edge exactly "
        "once, and where it should start. Rules, in order: if there are no edges output 16777215; if the vertices of "
        "nonzero degree do not all lie in one connected component output 16777215; let the odd vertices be those with "
        "an odd number of incident edges: if there are none (an Euler circuit exists) output the smallest vertex id of "
        "nonzero degree; if there are exactly two (an Euler trail exists) output the smaller of those two ids; "
        "otherwise output 16777215. Isolated vertices (degree 0) are ignored.",
        tup(u24, E2), u24, _euler, _gen_euler, S, T,
        edges=[(0, []), (3, []), (2, [(1, 0)]), (4, [(1, 2), (2, 3), (3, 1)]), (4, [(0, 1), (2, 3)]),
               (4, [(0, 1), (0, 2), (0, 3)]), (5, [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)]),
               (4, [(3, 2), (2, 1)])],
        pre=und_ok(False))


# ================================================================ 22. number of shortest paths
def _nsp(x):
    n, s, t, edges = x
    if s >= n or t >= n: return 0
    adj = _adj(n, edges)
    d = [INF] * n; c = [0] * n; d[s] = 0; c[s] = 1; q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if d[v] == INF: d[v] = d[u] + 1; q.append(v)
            if d[v] == d[u] + 1: c[v] = (c[v] + c[u]) & M
    return c[t]


def _grid(r, n):
    """A grid-like graph (rows of width w) with a few edges dropped: many equal-length shortest paths."""
    w = max(1, int(n ** 0.5))
    es = []
    for v in range(n):
        if (v + 1) % w and v + 1 < n: es.append((v, v + 1))
        if v + w < n: es.append((v, v + w))
    es = [e for e in es if r.random() < 0.9]
    perm = list(range(n)); r.shuffle(perm)
    es = [_orient(r, perm[a], perm[b]) for a, b in es]; r.shuffle(es)
    return es


def _gen_nsp(r, n):
    es = _grid(r, n) if r.random() < 0.5 else rand_und(r, n)
    return (n, vtx(r, n), vtx(r, n), es)


program("t3_count_shortest_paths", "T3",
        f"{UND} unweighted graph. Input is (n, s, t, edges) with edges (u, v). Output the number of distinct shortest "
        "paths from s to t (paths with the minimum number of edges; two paths differ if their vertex sequences differ), "
        "mod 2^24. s == t (with s < n) gives 1. If t is unreachable from s, or s >= n, or t >= n, output 0.",
        tup(u24, u24, u24, E2), u24, _nsp, _gen_nsp, S, T,
        edges=[(0, 0, 0, []), (1, 0, 0, []), (2, 0, 1, []), (2, 0, 1, [(1, 0)]),
               (4, 0, 3, [(0, 1), (0, 2), (1, 3), (2, 3)]), (4, 0, 3, [(0, 1), (0, 2), (1, 3), (2, 3), (0, 3)]),
               (3, 0, 9, [(0, 1)])],
        pre=und_ok(False))


# ================================================================ 23. maximum flow
def _maxflow(x):
    n, s, t, edges = x
    if s >= n or t >= n or s == t: return 0
    cap = [dict() for _ in range(n)]
    for u, v, w in edges:
        cap[u][v] = cap[u].get(v, 0) + w
        cap[v].setdefault(u, 0)
    flow = 0
    while True:
        par = {s: None}; q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v, c in cap[u].items():
                if c > 0 and v not in par: par[v] = u; q.append(v)
        if t not in par: return flow & M
        b, v = INF, t
        while par[v] is not None: b = min(b, cap[par[v]][v]); v = par[v]
        v = t
        while par[v] is not None:
            u = par[v]; cap[u][v] -= b; cap[v][u] += b; v = u
        flow += b


program("t3_max_flow", "T3",
        f"{DIR} weighted graph read as a flow network. Input is (n, s, t, edges) with edges (u, v, w) meaning an arc "
        "u -> v of capacity w (arcs u -> v and v -> u may both exist, each with its own capacity). Output the value of "
        "a maximum flow from source s to sink t (equivalently the minimum total capacity of arcs whose removal leaves "
        "no directed path from s to t), mod 2^24. If s == t, or s >= n, or t >= n, output 0.",
        tup(u24, u24, u24, E3), u24, _maxflow,
        lambda r, n: (n, vtx(r, n), vtx(r, n), rand_dir(r, n, weighted=True)), S, T,
        edges=[(0, 0, 0, []), (2, 0, 0, [(0, 1, 5)]), (2, 0, 1, [(0, 1, 5)]), (2, 1, 0, [(0, 1, 5)]),
               (4, 0, 3, [(0, 1, 3), (0, 2, 2), (1, 3, 2), (2, 3, 3), (1, 2, 1)]),
               (3, 0, 2, [(0, 1, 10), (1, 2, 4), (0, 2, 1), (2, 1, 7)]), (2, 0, 5, [(0, 1, 5)])],
        pre=dir_ok(True))


# ================================================================ 24. k-core size
def _kcore(x):
    n, k, edges = x
    nb = [set() for _ in range(n)]
    for u, v in edges: nb[u].add(v); nb[v].add(u)
    alive = [True] * n
    q = deque(v for v in range(n) if len(nb[v]) < k)
    deg = [len(s) for s in nb]
    while q:
        v = q.popleft()
        if not alive[v]: continue
        alive[v] = False
        for u in nb[v]:
            if alive[u]:
                deg[u] -= 1
                if deg[u] < k: q.append(u)
    return sum(alive)


def _gen_kcore(r, n):
    m = r.randint(0, n * (n - 1) // 2) if n <= 8 else r.randint(n, 3 * n)
    return (n, r.randint(0, 5), rand_und(r, n, m=m))


program("t3_kcore_size", "T3",
        f"{UND} unweighted graph. Input is (n, k, edges) with edges (u, v). Repeatedly delete any vertex whose degree in "
        "the current remaining graph (counting only edges to vertices not yet deleted) is less than k, until every "
        "remaining vertex has degree >= k. Output the number of vertices that remain (the size of the k-core; the "
        "result does not depend on deletion order). k = 0 gives n.",
        tup(u24, u24, E2), u24, _kcore, _gen_kcore, S, T,
        edges=[(0, 0, []), (3, 0, []), (3, 1, []), (2, 1, [(0, 1)]), (3, 2, [(0, 1), (1, 2)]),
               (4, 2, [(0, 1), (1, 2), (2, 0), (2, 3)]), (4, 3, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])],
        pre=und_ok(False))


# ================================================================ 25. lexicographically first optimal path
def _lexpath(x):
    n, s, t, edges = x
    if s >= n or t >= n: return []
    adj = _adj(n, edges)
    import heapq
    D = [(INF, INF)] * n; D[t] = (0, 0); h = [((0, 0), t)]
    while h:
        d, u = heapq.heappop(h)
        if d > D[u]: continue
        for v, w in adj[u]:
            nd = (d[0] + w, d[1] + 1)
            if nd < D[v]: D[v] = nd; heapq.heappush(h, (nd, v))
    if D[s][0] == INF: return []
    path = [s]; u = s
    while u != t:
        u = min(v for v, w in adj[u] if D[v][0] != INF and (D[v][0] + w, D[v][1] + 1) == D[u])
        path.append(u)
    return path


program("t3_lex_shortest_path", "T3",
        f"{UND} weighted graph. Input is (n, s, t, edges) with edges (u, v, w). Output one path from s to t as the list "
        "of its vertices, starting with s and ending with t, chosen as follows: minimum total edge weight; among those, "
        "the fewest edges; among those, the lexicographically smallest vertex sequence (compare the lists position by "
        "position, smaller vertex id first at the first difference). s == t (with s < n) gives [s]. If t is unreachable "
        "from s, or s >= n, or t >= n, output the empty list.",
        tup(u24, u24, u24, E3), L, _lexpath,
        lambda r, n: (n, vtx(r, n), vtx(r, n), rand_und(r, n, weighted=True)), S, T,
        edges=[(0, 0, 0, []), (1, 0, 0, []), (2, 0, 1, []), (2, 1, 0, [(0, 1, 3)]),
               (4, 0, 3, [(0, 2, 1), (2, 3, 1), (0, 1, 1), (1, 3, 1)]), (3, 0, 2, [(0, 1, 1), (1, 2, 1), (0, 2, 2)]),
               (5, 0, 4, [(0, 3, 1), (3, 4, 1), (0, 1, 1), (1, 2, 1), (2, 4, 1), (0, 2, 2)]),
               (3, 0, 7, [(0, 1, 1)])],
        pre=und_ok(True))
