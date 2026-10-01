"""T5 Reconciliation kernels, part B (25 programs): CONFLICT, PROPERTY, REWRITE, METRIC and PIPELINE.

Each kernel is one step (or a composition of steps) of the reconciliation function in docs/RECONCILIATION-SPEC.md.
The DECIDE and CLUSTER kernels live in t5_a.py. Every description below is a complete contract on its own.
"""
from collections import Counter
from . import program
from ..types import u24, list_of, tup, MASK

M = MASK
BIG = MASK  # 16777215
L = list_of(u24)
PAIRS = list_of(tup(u24, u24))
TRIPLES = list_of(tup(u24, u24, u24))
S = list(range(0, 10))
TS = [72, 144]

# ---------------------------------------------------------------- contract fragments (joined into complete descriptions)
CLUST = ("A clustering c is a list of length n (nodes are 0..n-1) where c[i] is the canonical id of node i's cluster: "
         "nodes i and j are in the same cluster iff c[i] == c[j], and a cluster's canonical id is its largest node id "
         "(so c[i] >= i and c[c[i]] == c[i]). ")
MNL = ("Must-not-link pairs are (a, b) with a < b < n, no pair listed twice, in arbitrary order. ")
CANDS = ("Candidate pairs are triples (u, v, score) with u < v < n and 0 <= score <= 1000. ")
ORDER = ("Process the pairs one at a time in this order: descending score, ties by ascending u, then ascending v. "
         "Start with every node in its own singleton cluster. For pair (u, v): if u and v are already in the same cluster "
         "do nothing (this is not a skip). Otherwise let A be u's cluster and B be v's cluster; ")
ATTRS = ("Attributes are triples (node, key, value) with node < n, key in 0..3, any value; each (node, key) occurs at most "
         "once; list order is arbitrary. A node may lack some keys. ")
MAJ = ("The merged value of a key in a cluster is the value carried by the most attribute triples of that key among the "
       "cluster's nodes; ties go to the smallest value. ")
EDGES = ("Edges are undirected pairs (u, v) with u, v < n in either order; self loops (u == v) and repeated edges may occur. "
         "Rewriting maps edge (u, v) to (min(c[u], c[v]), max(c[u], c[v])), drops it if c[u] == c[v] (self loop), and "
         "collapses duplicates, so the rewritten graph is a set of pairs (x, y) with x < y. ")
DECIDE = ("Decide: a pair may appear several times in the candidate list; for each distinct (u, v) keep only its highest "
          "score; the pair is accepted iff that score >= tau. ")
LEX = "sorted ascending lexicographically (by first component, then second, then third)"


# ---------------------------------------------------------------- helpers
def _find(p, x):
    while p[x] != x:
        p[x] = p[p[x]]
        x = p[x]
    return x


def _canon_from_pairs(n, pairs):
    p = list(range(n))
    for u, v in pairs:
        a, b = _find(p, u), _find(p, v)
        if a != b: p[a] = b
    top = {}
    for i in range(n):
        r = _find(p, i); top[r] = max(top.get(r, i), i)
    return [top[_find(p, i)] for i in range(n)]


def _greedy(n, mnl, cands, cap=None):
    """Constrained greedy merge. Returns (canonical list, skipped pairs in processing order)."""
    order = sorted(cands, key=lambda t: (-t[2], t[0], t[1]))
    p = list(range(n)); mem = {i: {i} for i in range(n)}; skipped = []
    for u, v, _ in order:
        a, b = _find(p, u), _find(p, v)
        if a == b: continue
        A, B = mem[a], mem[b]
        bad = any((x in A and y in B) or (x in B and y in A) for x, y in mnl)
        if bad or (cap is not None and len(A) + len(B) > cap):
            skipped.append((u, v)); continue
        p[a] = b; mem[b] = A | B; del mem[a]
    top = {r: max(s) for r, s in mem.items()}
    return [top[_find(p, i)] for i in range(n)], skipped


def _decide(tau, cands):
    best = {}
    for u, v, s in cands:
        if (u, v) not in best or s > best[(u, v)]: best[(u, v)] = s
    return [(u, v, s) for (u, v), s in best.items() if s >= tau]


def _rewrite(c, edges):
    return sorted({(min(c[u], c[v]), max(c[u], c[v])) for u, v in edges if c[u] != c[v]})


def _merged(c, attrs):
    g = {}
    for node, k, val in attrs:
        g.setdefault((c[node], k), Counter())[val] += 1
    out = []
    for (cn, k), cnt in sorted(g.items()):
        top = max(cnt.values())
        out.append((cn, k, min(v for v, x in cnt.items() if x == top)))
    return out


# ---------------------------------------------------------------- preconditions
def _canon_ok(c):
    n = len(c)
    return all(0 <= x < n and x >= i and c[x] == x for i, x in enumerate(c))

def _mnl_ok(n, mnl):
    return all(a < b < n for a, b in mnl) and len(set(mnl)) == len(mnl)

def _cands_ok(n, cands, distinct=False):
    ok = all(u < v < n and 0 <= s <= 1000 for u, v, s in cands)
    return ok and (not distinct or len({(u, v) for u, v, _ in cands}) == len(cands))

def _attrs_ok(n, attrs):
    return all(x < n and k < 4 for x, k, _ in attrs) and len({(x, k) for x, k, _ in attrs}) == len(attrs)

def _edges_ok(n, edges):
    return all(e[0] < n and e[1] < n for e in edges)

def _acyclic(p):
    n = len(p)
    if not all(x < n for x in p): return False
    for i in range(n):
        x, steps = i, 0
        while p[x] != x:
            x = p[x]; steps += 1
            if steps > n: return False
    return True


# ---------------------------------------------------------------- generators: a small ground-truth world
def _world(r, n):
    nodes = list(range(n)); r.shuffle(nodes)
    groups, i = [], 0
    while i < n:
        s = r.choices([1, 2, 3, 4, 5, 6, 8], [30, 28, 18, 12, 5, 4, 3])[0]
        groups.append(sorted(nodes[i:i + s])); i += s
    truth = [0] * n
    for g in groups:
        for x in g: truth[x] = g[-1]
    return groups, truth


def _clamp(x): return max(0, min(1000, int(x)))


def _cands(r, n, groups, truth, dups=False):
    """Noisy candidate triples, distinct pairs unless dups; true and false scores overlap."""
    total = n * (n - 1) // 2
    k = min(total, r.randint(n // 2, 3 * n)) if n > 1 else 0
    true_pairs = [(a, b) for g in groups for j, a in enumerate(g) for b in g[j + 1:]]
    r.shuffle(true_pairs)
    chosen = {}
    for a, b in true_pairs[:max(0, min(len(true_pairs), (k * 3) // 5))]:
        chosen[(a, b)] = _clamp(r.gauss(700, 170))
    tries = 0
    while len(chosen) < k and tries < 20 * k + 20:
        tries += 1
        a, b = r.randrange(n), r.randrange(n)
        if a == b: continue
        a, b = min(a, b), max(a, b)
        if (a, b) in chosen: continue
        chosen[(a, b)] = _clamp(r.gauss(700, 170) if truth[a] == truth[b] else r.gauss(380, 200))
    out = [(a, b, s) for (a, b), s in chosen.items()]
    if dups and out:
        for _ in range(r.randint(0, max(1, len(out) // 8))):
            a, b, s = r.choice(out)
            out.append((a, b, _clamp(s + r.randint(-250, 250))))
    r.shuffle(out)
    return out


def _mnl(r, n, truth, cands):
    """Mostly true negatives, plus a few that block high-scoring false merges."""
    out = set()
    if n < 2: return []
    for _ in range(r.randint(0, max(1, n // 3))):
        a, b = r.randrange(n), r.randrange(n)
        if a != b and truth[a] != truth[b]: out.add((min(a, b), max(a, b)))
    for u, v, s in cands:
        if s >= 500 and truth[u] != truth[v] and r.random() < 0.5: out.add((u, v))
    if r.random() < 0.15:  # an occasional wrong constraint inside a true cluster
        a, b = r.randrange(n), r.randrange(n)
        if a != b: out.add((min(a, b), max(a, b)))
    out = sorted(out); r.shuffle(out)
    return out


def _pred(r, n, cands):
    tau = r.randint(380, 720)
    return _canon_from_pairs(n, [(u, v) for u, v, s in cands if s >= tau])


def _edges(r, n, weighted=False):
    if n == 0: return []
    m = r.randint(0, 2 * n)
    out = []
    for _ in range(m):
        u = r.randrange(n)
        v = u if r.random() < 0.05 else r.randrange(n)
        out.append((u, v, r.randint(0, 100)) if weighted else (u, v))
    if out and r.random() < 0.5:
        out += [r.choice(out) for _ in range(r.randint(1, 3))]
    r.shuffle(out)
    return out


def _attrs(r, n, truth):
    true_val = {}
    out = []
    for x in range(n):
        for k in range(4):
            if r.random() < 0.55:
                tv = true_val.setdefault((truth[x], k), r.randrange(6))
                out.append((x, k, tv if r.random() < 0.8 else r.randrange(6)))
    r.shuffle(out)
    return out


def _clustering(r, n):
    """A predicted clustering (often imperfect) or the ground truth, plus the world it came from."""
    groups, truth = _world(r, n)
    cands = _cands(r, n, groups, truth)
    c = _pred(r, n, cands) if r.random() < 0.8 else truth
    return c, groups, truth, cands


def _gen_c_mnl(r, n):
    c, _, truth, cands = _clustering(r, n)
    return (c, _mnl(r, n, truth, cands))


def _gen_greedy(r, n, cap=False):
    groups, truth = _world(r, n)
    cands = _cands(r, n, groups, truth)
    tau = r.randint(350, 650)
    acc = [t for t in cands if t[2] >= tau]
    mnl = _mnl(r, n, truth, acc)
    if cap:
        return (n, r.choice([1, 2, 2, 3, 3, 4, 5, 8, max(n, 1)]), mnl, acc)
    return (n, mnl, acc)


def _gen_c_attrs(r, n):
    c, _, truth, _ = _clustering(r, n)
    return (c, _attrs(r, n, truth))


def _gen_c_edges(r, n, weighted=False):
    c, _, _, _ = _clustering(r, n)
    return (c, _edges(r, n, weighted))


def _pointers(r, n, cyclic=False):
    order = list(range(n)); r.shuffle(order)
    p = list(range(n))
    for idx, x in enumerate(order):
        if idx > 0 and r.random() < 0.7: p[x] = order[r.randrange(idx)]
    if cyclic and n >= 2:
        k = r.randint(2, min(n, 5))
        cyc = r.sample(range(n), k)
        for j in range(k): p[cyc[j]] = cyc[(j + 1) % k]
    return p


def _gen_pipeline(r, n, edges=False, attrs=False):
    groups, truth = _world(r, n)
    cands = _cands(r, n, groups, truth, dups=True)
    mnl = _mnl(r, n, truth, cands)
    tau = r.choice([r.randint(350, 750)] * 6 + [0, 1001])
    out = (n, tau, mnl, cands)
    if edges: out += (_edges(r, n),)
    if attrs: out += (_attrs(r, n, truth),)
    return out


# ================================================================ CONFLICT
def _conflict_pairs(a):
    c, mnl = a
    return sorted((x, y) for x, y in mnl if c[x] == c[y])

_pre_c_mnl = lambda a: _canon_ok(a[0]) and _mnl_ok(len(a[0]), a[1])
E_C_MNL = [([], []), ([0], []), ([1, 1], [(0, 1)]), ([0, 1], [(0, 1)]),
           ([2, 2, 2, 3], [(0, 3), (1, 2), (0, 1)]), ([1, 1, 3, 3], [(2, 3), (0, 2)]),
           ([4, 4, 4, 4, 4], [(3, 4), (0, 1), (1, 4), (2, 3)])]

program("t5_conflict_count", "T5",
        "Input is (c, mnl). " + CLUST + MNL +
        "A must-not-link pair (a, b) is violated when c[a] == c[b]. Output the number of violated must-not-link pairs.",
        tup(L, PAIRS), u24, lambda a: len(_conflict_pairs(a)), _gen_c_mnl, S, TS, edges=E_C_MNL, pre=_pre_c_mnl)

program("t5_conflict_pairs", "T5",
        "Input is (c, mnl). " + CLUST + MNL +
        "A must-not-link pair (a, b) is violated when c[a] == c[b]. Output the violated pairs (a, b) as they appear "
        "(a < b), " + LEX + ". No violations gives [].",
        tup(L, PAIRS), PAIRS, _conflict_pairs, _gen_c_mnl, S, TS, edges=E_C_MNL, pre=_pre_c_mnl)

def _conflict_flags(a):
    c, mnl = a
    bad = {c[x] for x, y in mnl if c[x] == c[y]}
    return [1 if k in bad else 0 for k in sorted(set(c))]
program("t5_conflict_flags", "T5",
        "Input is (c, mnl). " + CLUST + MNL +
        "Output one entry per cluster, clusters ordered by ascending canonical id: 1 if the cluster contains both ends "
        "of at least one must-not-link pair, else 0. The output length is the number of distinct values in c; n = 0 gives [].",
        tup(L, PAIRS), L, _conflict_flags, _gen_c_mnl, S, TS, edges=E_C_MNL, pre=_pre_c_mnl)

GREEDY_OUT = ("After all pairs, output a list of length n whose entry i is the largest node id in node i's final cluster.")
E_GREEDY = [(0, [], []), (1, [], []), (2, [(0, 1)], [(0, 1, 900)]), (2, [], [(0, 1, 0)]),
            (3, [(0, 2)], [(0, 1, 500), (1, 2, 900)]),
            (4, [(0, 3)], [(1, 3, 700), (0, 1, 700), (2, 3, 100)]),
            (5, [(0, 4), (1, 2)], [(0, 1, 800), (2, 3, 800), (1, 3, 800), (3, 4, 600), (0, 4, 1000)]),
            (6, [], [(0, 1, 5), (1, 2, 5), (2, 3, 5), (3, 4, 5), (4, 5, 5)])]
_pre_greedy = lambda a: _mnl_ok(a[0], a[1]) and _cands_ok(a[0], a[2], distinct=True)

program("t5_conflict_greedy", "T5",
        "Constrained greedy merge. Input is (n, mnl, cands). " + MNL + CANDS +
        "Every (u, v) occurs at most once in cands and every pair is to be merged unless it conflicts. " + ORDER +
        "the merge is skipped if some must-not-link pair has one end in A and the other end in B; otherwise A and B "
        "become one cluster. Clusters only grow, so a skipped merge is never retried. " + GREEDY_OUT,
        tup(u24, PAIRS, TRIPLES), L, lambda a: _greedy(a[0], a[1], a[2])[0],
        lambda r, n: _gen_greedy(r, n), S, TS, edges=E_GREEDY, pre=_pre_greedy)

E_CAP = [(n, cap, m, cs) for cap, (n, m, cs) in zip([1, 2, 3, 2, 2, 3, 3, 4], [e for e in E_GREEDY])] + \
        [(3, 0, [], [(0, 1, 10)]), (6, 3, [], [(0, 1, 9), (2, 3, 9), (1, 2, 8), (4, 5, 7), (3, 4, 6)]),
         (4, 16777215, [(0, 3)], [(0, 1, 1), (1, 2, 2), (2, 3, 3)])]
_pre_cap = lambda a: _mnl_ok(a[0], a[2]) and _cands_ok(a[0], a[3], distinct=True)

program("t5_conflict_greedy_cap", "T5",
        "Constrained greedy merge with a size cap. Input is (n, cap, mnl, cands). " + MNL + CANDS +
        "Every (u, v) occurs at most once in cands and every pair is to be merged unless it conflicts. " + ORDER +
        "the merge is skipped if some must-not-link pair has one end in A and the other end in B, or if "
        "|A| + |B| > cap (number of nodes); otherwise A and B become one cluster. Clusters only grow, so a skipped merge "
        "is never retried. cap may be 0 (every merge skipped) or larger than n (no cap). " + GREEDY_OUT,
        tup(u24, u24, PAIRS, TRIPLES), L, lambda a: _greedy(a[0], a[2], a[3], a[1])[0],
        lambda r, n: _gen_greedy(r, n, cap=True), S, TS, edges=E_CAP, pre=_pre_cap)

program("t5_conflict_skipped", "T5",
        "The merges a capped constrained greedy merge rejects. Input is (n, cap, mnl, cands). " + MNL + CANDS +
        "Every (u, v) occurs at most once in cands. " + ORDER +
        "the merge is skipped if some must-not-link pair has one end in A and the other end in B, or if "
        "|A| + |B| > cap (number of nodes); otherwise A and B become one cluster. Pairs whose ends are already in one "
        "cluster are not skips. Output the skipped pairs as (u, v), in the order they were processed (not re-sorted). "
        "No skips gives [].",
        tup(u24, u24, PAIRS, TRIPLES), PAIRS, lambda a: _greedy(a[0], a[2], a[3], a[1])[1],
        lambda r, n: _gen_greedy(r, n, cap=True), S, TS, edges=E_CAP, pre=_pre_cap)


# ================================================================ PROPERTY
_pre_c_attrs = lambda a: _canon_ok(a[0]) and _attrs_ok(len(a[0]), a[1])
E_C_ATTRS = [([], []), ([0], []), ([0], [(0, 3, 7)]), ([1, 1], [(0, 0, 5), (1, 0, 5)]),
             ([1, 1], [(1, 0, 4), (0, 0, 5)]), ([2, 2, 2], [(0, 1, 9), (1, 1, 3), (2, 1, 9), (2, 0, 1)]),
             ([1, 1, 3, 3], [(3, 2, 6), (2, 2, 2), (0, 2, 2), (1, 3, 0), (0, 3, 0), (1, 2, 8)]),
             ([0, 1, 2], [(0, 0, 1), (1, 0, 2), (2, 0, 3)])]

def _prop_conflict_keys(a):
    c, attrs = a
    vals = {}
    for x, k, v in attrs: vals.setdefault((c[x], k), set()).add(v)
    return sorted(ck for ck, vs in vals.items() if len(vs) > 1)

program("t5_prop_conflicts", "T5",
        "Property-conflict count. Input is (c, attrs). " + CLUST + ATTRS +
        "For a cluster and a key, collect the values of that key over all nodes of the cluster; the (cluster, key) is a "
        "property conflict if it has more than one distinct value. Output the number of conflicting (cluster, key) "
        "combinations, summed over all clusters and keys.",
        tup(L, TRIPLES), u24, lambda a: len(_prop_conflict_keys(a)), _gen_c_attrs, S, TS, edges=E_C_ATTRS, pre=_pre_c_attrs)

program("t5_prop_conflict_keys", "T5",
        "Property-conflict list. Input is (c, attrs). " + CLUST + ATTRS +
        "For a cluster and a key, collect the values of that key over all nodes of the cluster; the (cluster, key) is a "
        "property conflict if it has more than one distinct value. Output every conflicting combination as "
        "(canonical id, key), " + LEX + ". No conflicts gives [].",
        tup(L, TRIPLES), PAIRS, _prop_conflict_keys, _gen_c_attrs, S, TS, edges=E_C_ATTRS, pre=_pre_c_attrs)

def _prop_majority(a):
    cn, key, c, attrs = a
    cnt = Counter(v for x, k, v in attrs if k == key and c[x] == cn)
    if not cnt: return BIG
    top = max(cnt.values())
    return min(v for v, x in cnt.items() if x == top)

def _gen_majority(r, n):
    c, attrs = _gen_c_attrs(r, n)
    if attrs and r.random() < 0.85:
        x, k, _ = r.choice(attrs); return (c[x], k, c, attrs)
    return (r.choice(c) if c and r.random() < 0.7 else r.randrange(n + 2), r.randrange(4), c, attrs)

program("t5_prop_majority", "T5",
        "Majority merge of one property. Input is (k, key, c, attrs) with key in 0..3. " + CLUST + ATTRS +
        "The cluster is the set of nodes i with c[i] == k (possibly empty if k is not a canonical id). " + MAJ +
        "Output the merged value of `key` in that cluster, or 16777215 if no node of the cluster has that key.",
        tup(u24, u24, L, TRIPLES), u24, _prop_majority, _gen_majority, S, TS,
        edges=[(0, 0, [], []), (0, 0, [0], []), (0, 3, [0], [(0, 3, 7)]), (1, 0, [1, 1], [(1, 0, 4), (0, 0, 5)]),
               (2, 1, [2, 2, 2], [(0, 1, 9), (1, 1, 3), (2, 1, 9), (2, 0, 1)]), (2, 2, [2, 2, 2], [(0, 1, 9)]),
               (1, 0, [0, 1, 2], [(0, 0, 1), (1, 0, 2), (2, 0, 3)]), (5, 0, [0, 1], [(0, 0, 1)]),
               (3, 2, [1, 1, 3, 3], [(3, 2, 6), (2, 2, 2), (0, 2, 2), (1, 3, 0), (0, 3, 0), (1, 2, 8)])],
        pre=lambda a: a[1] < 4 and _canon_ok(a[2]) and _attrs_ok(len(a[2]), a[3]))

program("t5_prop_merged", "T5",
        "Merged attribute table. Input is (c, attrs). " + CLUST + ATTRS + MAJ +
        "Output one triple (canonical id, key, merged value) for every cluster and key such that at least one node of the "
        "cluster has that key, " + LEX + " (i.e. by canonical id, then key). No attributes gives [].",
        tup(L, TRIPLES), TRIPLES, lambda a: _merged(*a), _gen_c_attrs, S, TS, edges=E_C_ATTRS, pre=_pre_c_attrs)

program("t5_prop_distinct_per_key", "T5",
        "Input is attrs, a list of (node, key, value) triples with key in 0..3 (any node and value, any order, "
        "repeats allowed). Output a list of exactly 4 counts: entry k is the number of distinct values that key k takes "
        "over the whole list (0 if key k never occurs).",
        TRIPLES, L, lambda at: [len({v for _, k, v in at if k == key}) for key in range(4)],
        lambda r, n: _attrs(r, n, _world(r, n)[1]), S, TS,
        edges=[[], [(0, 0, 1)], [(0, 3, 1), (1, 3, 1), (2, 3, 2)], [(0, 0, 5), (0, 1, 5), (0, 2, 5), (0, 3, 5)],
               [(4, 2, 0), (1, 2, 16777215), (4, 2, 0)]],
        pre=lambda at: all(k < 4 for _, k, _ in at))


# ================================================================ REWRITE
_pre_c_edges = lambda a: _canon_ok(a[0]) and _edges_ok(len(a[0]), a[1])
E_C_EDGES = [([], []), ([0], []), ([0], [(0, 0)]), ([0, 1], [(0, 1)]), ([0, 1], [(1, 0), (0, 1), (1, 0)]),
             ([1, 1], [(0, 1), (1, 0)]), ([1, 1, 2, 3], [(0, 2), (1, 2), (3, 0), (2, 3), (3, 3)]),
             ([2, 2, 2, 4, 4], [(0, 3), (1, 4), (2, 0), (4, 1), (3, 4)])]

program("t5_rewrite_edges", "T5",
        "Edge rewrite. Input is (c, edges). " + CLUST + EDGES +
        "Output the rewritten edge set as distinct pairs (x, y) with x < y, " + LEX + ".",
        tup(L, PAIRS), PAIRS, lambda a: _rewrite(*a), _gen_c_edges, S, TS, edges=E_C_EDGES, pre=_pre_c_edges)

def _rewrite_w(a):
    c, edges = a
    acc = {}
    for u, v, w in edges:
        if c[u] != c[v]:
            key = (min(c[u], c[v]), max(c[u], c[v])); acc[key] = (acc.get(key, 0) + w) & M
    return [(x, y, w) for (x, y), w in sorted(acc.items())]

program("t5_rewrite_weighted", "T5",
        "Weighted edge rewrite. Input is (c, edges) with edges as triples (u, v, w). " + CLUST +
        "Edges are undirected with u, v < n in either order and an integer weight w; self loops and repeated edges may occur. "
        "Each edge maps to (min(c[u], c[v]), max(c[u], c[v])); edges with c[u] == c[v] are dropped together with their "
        "weight. Output one triple (x, y, total) per distinct rewritten pair, where total is the sum mod 2^24 of the "
        "weights of all edges mapped to (x, y) (a total may be 0), " + LEX + ".",
        tup(L, TRIPLES), TRIPLES, _rewrite_w, lambda r, n: _gen_c_edges(r, n, True), S, TS,
        edges=[([], []), ([0], [(0, 0, 5)]), ([0, 1], [(0, 1, 3), (1, 0, 4)]), ([0, 1], [(0, 1, 0)]),
               ([1, 1, 2], [(0, 2, 1), (2, 1, 2), (1, 0, 50)]), ([0, 1], [(0, 1, 16777215), (1, 0, 2)]),
               ([2, 2, 2, 4, 4], [(0, 3, 1), (1, 4, 2), (2, 0, 3), (4, 1, 4), (3, 4, 5)])],
        pre=lambda a: _canon_ok(a[0]) and _edges_ok(len(a[0]), a[1]))

program("t5_rewrite_collapsed", "T5",
        "Number of edges collapsed by the rewrite. Input is (c, edges). " + CLUST + EDGES +
        "Output len(edges) minus the number of distinct rewritten pairs, i.e. how many input edges disappear as self "
        "loops or duplicates.",
        tup(L, PAIRS), u24, lambda a: len(a[1]) - len(_rewrite(*a)), _gen_c_edges, S, TS, edges=E_C_EDGES, pre=_pre_c_edges)

def _degrees(a):
    c, edges = a
    deg = Counter()
    for x, y in _rewrite(c, edges): deg[x] += 1; deg[y] += 1
    return [deg[k] for k in sorted(set(c))]

program("t5_rewrite_degrees", "T5",
        "Degrees of the merged graph. Input is (c, edges). " + CLUST + EDGES +
        "The merged graph's nodes are the clusters. Output one entry per cluster, clusters ordered by ascending canonical "
        "id: the number of distinct rewritten pairs that contain its canonical id (= its number of distinct neighbouring "
        "clusters; 0 if none). The output length is the number of distinct values in c.",
        tup(L, PAIRS), L, _degrees, _gen_c_edges, S, TS, edges=E_C_EDGES, pre=_pre_c_edges)

def _neigh(a):
    k, c, edges = a
    out = set()
    for x, y in _rewrite(c, edges):
        if x == k: out.add(y)
        if y == k: out.add(x)
    return sorted(out)

def _gen_neigh(r, n):
    c, e = _gen_c_edges(r, n)
    k = r.choice(c) if c and r.random() < 0.85 else r.randrange(n + 2)
    if e and r.random() < 0.6: k = c[r.choice(e)[0]]
    return (k, c, e)

program("t5_rewrite_neighbours", "T5",
        "Neighbours of one cluster in the merged graph. Input is (k, c, edges). " + CLUST + EDGES +
        "Output the canonical ids adjacent to k in the rewritten graph (every y with (k, y) or (y, k) a rewritten pair), "
        "distinct, ascending. k never neighbours itself. If k is not a canonical id or has no edges, output [].",
        tup(u24, L, PAIRS), L, _neigh, _gen_neigh, S, TS,
        edges=[(0, [], []), (0, [0], [(0, 0)]), (1, [0, 1], [(1, 0)]), (0, [0, 1], [(1, 0), (0, 1)]),
               (2, [1, 1, 2, 3], [(0, 2), (1, 2), (3, 0), (2, 3), (3, 3)]), (1, [1, 1, 2, 3], [(3, 0), (2, 0), (1, 0)]),
               (4, [2, 2, 2, 4, 4], [(0, 3), (1, 4), (2, 0), (4, 1)]), (7, [0, 1], [(0, 1)])],
        pre=lambda a: _canon_ok(a[1]) and _edges_ok(len(a[1]), a[2]))

def _roots(p):
    out = []
    for i in range(len(p)):
        x = i
        while p[x] != x: x = p[x]
        out.append(x)
    return out

program("t5_rewrite_sameas_roots", "T5",
        "SAME_AS pointer resolution. Input is a pointer list p of length n with every p[i] < n; p[i] == i means node i is "
        "a root, otherwise i points to p[i]. The pointers are acyclic: following p from any node reaches a root after "
        "finitely many steps. Output a list of length n whose entry i is the root reached from i (i itself if i is a root). "
        "Pointers need not go to larger ids and chains may be long.",
        L, L, _roots, lambda r, n: _pointers(r, n), S, TS,
        edges=[[], [0], [1, 1], [0, 0], [1, 2, 2], [0, 0, 1, 2], [3, 3, 1, 3], [4, 0, 1, 2, 4], [1, 2, 3, 4, 4]],
        pre=_acyclic)

def _has_cycle(p):
    n = len(p)
    for i in range(n):
        x, steps = i, 0
        while p[x] != x:
            x = p[x]; steps += 1
            if steps > n: return 1
    return 0

program("t5_rewrite_sameas_cycle", "T5",
        "SAME_AS cycle detection. Input is a pointer list p of length n with every p[i] < n; p[i] == i means node i is "
        "a root (a self pointer is not a cycle), otherwise i points to p[i]. Output 1 if following pointers from some "
        "node never reaches a root (the pointers contain a cycle of two or more distinct nodes), else 0. [] gives 0.",
        L, u24, _has_cycle, lambda r, n: _pointers(r, n, cyclic=r.random() < 0.5), S, TS,
        edges=[[], [0], [1, 0], [1, 1], [1, 2, 0], [1, 2, 2], [0, 2, 3, 1], [0, 0, 3, 4, 3]],
        pre=lambda p: all(x < len(p) for x in p))


# ================================================================ METRIC
def _pair_counts(a):
    pred, truth = a
    tp = fp = fn = agree = 0
    n = len(pred)
    for i in range(n):
        for j in range(i + 1, n):
            sp, st = pred[i] == pred[j], truth[i] == truth[j]
            tp += sp and st; fp += sp and not st; fn += st and not sp; agree += sp == st
    return tp & M, fp & M, fn & M, agree & M

def _gen_metric(r, n):
    c, _, truth, _ = _clustering(r, n)
    if r.random() < 0.2:  # labels need not be canonical ids
        rel = {}
        c = [rel.setdefault(x, r.randrange(1000)) for x in c]
    return (c, truth)

E_METRIC = [([], []), ([5], [9]), ([1, 1], [1, 1]), ([0, 1], [1, 1]), ([1, 1], [0, 1]),
            ([2, 2, 2, 3], [1, 1, 3, 3]), ([7, 7, 8, 8, 8], [0, 1, 0, 1, 1]), ([0, 1, 2], [0, 1, 2])]
MET = ("Input is (pred, truth), two label lists of the same length n (node i has predicted label pred[i] and true label "
       "truth[i]); labels are arbitrary numbers and only equality matters. ")
_pre_metric = lambda a: len(a[0]) == len(a[1])

program("t5_metric_pairwise", "T5",
        "Pairwise clustering confusion counts. " + MET +
        "Over all unordered node pairs i < j: tp counts pairs with pred[i] == pred[j] and truth[i] == truth[j]; fp counts "
        "pairs with pred equal but truth different; fn counts pairs with truth equal but pred different. Output the tuple "
        "(tp, fp, fn), each mod 2^24.",
        tup(L, L), tup(u24, u24, u24), lambda a: _pair_counts(a)[:3], _gen_metric, S, TS, edges=E_METRIC, pre=_pre_metric)

def _purity(a):
    pred, truth = a
    g = {}
    for p_, t_ in zip(pred, truth): g.setdefault(p_, Counter())[t_] += 1
    return sum(max(cnt.values()) for cnt in g.values())

program("t5_metric_purity", "T5",
        "Cluster purity count. " + MET +
        "Group nodes by predicted label. For each predicted group take the largest number of its nodes that share one "
        "true label. Output the sum of these maxima over all predicted groups (n = 0 gives 0; a perfect clustering gives n).",
        tup(L, L), u24, _purity, _gen_metric, S, TS, edges=E_METRIC, pre=_pre_metric)

program("t5_metric_rand", "T5",
        "Rand agreement count. " + MET +
        "Over all unordered node pairs i < j, a pair agrees if (pred[i] == pred[j]) equals (truth[i] == truth[j]), i.e. "
        "both put the pair together or both keep it apart. Output the number of agreeing pairs mod 2^24.",
        tup(L, L), u24, lambda a: _pair_counts(a)[3], _gen_metric, S, TS, edges=E_METRIC, pre=_pre_metric)


# ================================================================ PIPELINE
def _recon_canon(a):
    n, tau, cands = a
    return _canon_from_pairs(n, [(u, v) for u, v, _ in _decide(tau, cands)])

def _recon_mnl(a):
    n, tau, mnl, cands = a[:4]
    return _greedy(n, mnl, _decide(tau, cands))[0]

def _recon_full(a):
    c = _recon_mnl(a)
    return (c, _rewrite(c, a[4]))

def _recon_props(a):
    c, e = _recon_full(a)
    return (c, e, _merged(c, a[5]))

PIPE_GREEDY = (ORDER.replace("Process the pairs", "Process the accepted pairs (each distinct pair once, with its kept "
                                                  "score)") +
               "the merge is skipped if some must-not-link pair has one end in A and the other end in B; otherwise A and B "
               "become one cluster (a skipped merge is never retried). The canonical id of a node is the largest node id "
               "in its final cluster. ")
E_PIPE = [(0, 500, [], []), (1, 0, [], []), (2, 500, [], [(0, 1, 499)]), (2, 500, [], [(0, 1, 499), (0, 1, 500)]),
          (3, 0, [(0, 2)], [(0, 1, 500), (1, 2, 900)]), (3, 1001, [], [(0, 1, 1000), (1, 2, 1000)]),
          (4, 600, [(0, 3)], [(1, 3, 700), (0, 1, 700), (2, 3, 100), (2, 3, 650), (1, 3, 600)]),
          (5, 300, [(0, 4), (1, 2)], [(0, 1, 800), (2, 3, 800), (1, 3, 800), (3, 4, 600), (0, 4, 1000), (0, 4, 1)])]

program("t5_reconcile_canon", "T5",
        "Decide then cluster. Input is (n, tau, cands). " + CANDS + DECIDE +
        "Cluster: the clusters are the connected components of the graph on nodes 0..n-1 whose edges are the accepted "
        "pairs (transitive closure; order does not matter). Output a list of length n whose entry i is the largest node "
        "id in node i's cluster (i itself if i is in no accepted pair).",
        tup(u24, u24, TRIPLES), L, _recon_canon, lambda r, n: (lambda g: (g[0], g[1], g[3]))(_gen_pipeline(r, n)), S, TS,
        edges=[(e[0], e[1], e[3]) for e in E_PIPE], pre=lambda a: _cands_ok(a[0], a[2]))

_pre_pipe = lambda a: _mnl_ok(a[0], a[2]) and _cands_ok(a[0], a[3])

program("t5_reconcile_canon_mnl", "T5",
        "Decide then conflict-aware cluster. Input is (n, tau, mnl, cands). " + MNL + CANDS + DECIDE + PIPE_GREEDY +
        "Output a list of length n whose entry i is node i's canonical id.",
        tup(u24, u24, PAIRS, TRIPLES), L, _recon_mnl, lambda r, n: _gen_pipeline(r, n), S, TS, edges=E_PIPE, pre=_pre_pipe)

E_PIPE_EDGES = [(0, 500, [], [], []), (1, 0, [], [], [(0, 0)]), (2, 500, [], [(0, 1, 499)], [(1, 0), (0, 1)]),
                (2, 500, [], [(0, 1, 499), (0, 1, 500)], [(1, 0), (0, 1)]),
                (3, 0, [(0, 2)], [(0, 1, 500), (1, 2, 900)], [(0, 1), (1, 2), (2, 0)]),
                (4, 600, [(0, 3)], [(1, 3, 700), (0, 1, 700), (2, 3, 100), (2, 3, 650), (1, 3, 600)],
                 [(0, 2), (1, 3), (3, 1), (2, 2), (0, 1)]),
                (5, 300, [(0, 4), (1, 2)], [(0, 1, 800), (2, 3, 800), (1, 3, 800), (3, 4, 600), (0, 4, 1000), (0, 4, 1)],
                 [(0, 4), (4, 0), (1, 2), (3, 0), (2, 4)])]
_pre_full = lambda a: _pre_pipe(a) and _edges_ok(a[0], a[4])
EDGE_REW = ("Edges are undirected pairs (u, v) with u, v < n in either order; self loops and repeats may occur. Rewrite: "
            "edge (u, v) maps to (min(C[u], C[v]), max(C[u], C[v])) where C is the canonical-id list, is dropped if "
            "C[u] == C[v], and duplicates collapse to one. ")

program("t5_reconcile_full", "T5",
        "Full reconciliation: decide, conflict-aware cluster, rewrite. Input is (n, tau, mnl, cands, edges). " + MNL + CANDS +
        DECIDE + PIPE_GREEDY + EDGE_REW +
        "Output the pair (C, E): C is the list of length n whose entry i is node i's canonical id, and E is the rewritten "
        "edge set as distinct pairs (x, y) with x < y, " + LEX + ".",
        tup(u24, u24, PAIRS, TRIPLES, PAIRS), tup(L, PAIRS), _recon_full, lambda r, n: _gen_pipeline(r, n, edges=True),
        S, TS, edges=E_PIPE_EDGES, pre=_pre_full)

E_PIPE_ATTRS = [e + (at,) for e, at in zip(E_PIPE_EDGES, [
    [], [(0, 3, 7)], [(0, 0, 5), (1, 0, 6)], [(0, 0, 5), (1, 0, 6)], [(0, 1, 2), (1, 1, 3), (2, 1, 3), (1, 0, 9)],
    [(0, 0, 4), (1, 0, 4), (3, 0, 1), (2, 2, 2), (3, 2, 1)], [(4, 3, 0), (0, 3, 1), (2, 1, 5), (3, 1, 5), (1, 1, 4)]])]

program("t5_reconcile_full_props", "T5",
        "Full reconciliation with property merge. Input is (n, tau, mnl, cands, edges, attrs). " + MNL + CANDS +
        DECIDE + PIPE_GREEDY + EDGE_REW + ATTRS +
        "The merged value of a key in a cluster is the value carried by the most attribute triples of that key among the "
        "cluster's nodes; ties go to the smallest value. Output the triple (C, E, P): C is the list of length n whose entry "
        "i is node i's canonical id; E is the rewritten edge set as distinct pairs (x, y) with x < y, " + LEX + "; P has "
        "one triple (canonical id, key, merged value) for every cluster and key such that at least one node of the "
        "cluster has that key, " + LEX + ".",
        tup(u24, u24, PAIRS, TRIPLES, PAIRS, TRIPLES), tup(L, PAIRS, TRIPLES), _recon_props,
        lambda r, n: _gen_pipeline(r, n, edges=True, attrs=True), S, TS, edges=E_PIPE_ATTRS,
        pre=lambda a: _pre_full(a) and _attrs_ok(a[0], a[5]))
