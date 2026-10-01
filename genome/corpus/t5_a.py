"""T5 (part a) Reconciliation: DECIDE and CLUSTER kernels (25 programs).

The reconciliation function is specified in docs/RECONCILIATION-SPEC.md. These are its decision step (threshold, dedup,
known-pair drop, processing order, caps, conformal singleton test, idempotent staging) and its clustering step
(union-find components, canonical id = largest member, SAME_AS emission, cluster statistics), one kernel each.
Every description is a complete contract on its own: node ids are 0..n-1, scores and tau are integers 0..1000.
"""
from . import program
from ..types import u24, list_of, tup

L = list_of(u24)
PAIR = tup(u24, u24)
PAIRS = list_of(PAIR)
TRI = tup(u24, u24, u24)
TRIS = list_of(TRI)
S = list(range(0, 10))
TS = [72, 144]


# ---------------------------------------------------------------- helpers (reference side)
def _roots(n, pairs):
    """root[i] = representative of i's component (union-find, path halving)."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for u, v in pairs:
        a, b = find(u), find(v)
        if a != b: parent[a] = b
    return [find(i) for i in range(n)]


def _clusters(n, pairs):
    """Clusters as ascending member lists, ordered by smallest member."""
    groups = {}
    for i, r in enumerate(_roots(n, pairs)):
        groups.setdefault(r, []).append(i)
    return sorted(groups.values(), key=lambda c: c[0])


def _order_key(t):
    return (-t[2], t[0], t[1])


# ---------------------------------------------------------------- generators
def _truth(rng, n):
    """Ground-truth partition of 0..n-1: sizes mostly 1-4, a few larger."""
    ids = list(range(n)); rng.shuffle(ids)
    out, i = [], 0
    while i < n:
        r = rng.random()
        s = 1 if r < .35 else 2 if r < .65 else 3 if r < .80 else 4 if r < .92 else rng.randint(5, 12)
        out.append(ids[i:i + s]); i += s
    return out


def _score(rng, true):
    s = rng.gauss(760, 150) if true else rng.gauss(380, 190)
    if rng.random() < 0.03: s = rng.choice([0, 1000])
    return max(0, min(1000, int(s)))


def _cands(rng, n, dup=True, rev=False, m=None):
    """Candidate triples: true pairs score high, false pairs low, the two overlap. Normalised u < v unless rev."""
    if n < 2: return []
    truth = _truth(rng, n)
    multi = [c for c in truth if len(c) >= 2]
    if m is None: m = rng.randint(0, 3 * n)
    out = []
    for _ in range(m):
        if dup and out and rng.random() < 0.1:
            a, b, s0 = rng.choice(out)
            u, v = min(a, b), max(a, b)
            s = s0 if rng.random() < 0.3 else _score(rng, rng.random() < 0.5)
        elif multi and rng.random() < 0.55:
            u, v = rng.sample(rng.choice(multi), 2); s = _score(rng, True)
        else:
            u, v = rng.sample(range(n), 2); s = _score(rng, False)
        if u > v: u, v = v, u
        if rev and rng.random() < 0.3: u, v = v, u
        out.append((u, v, s))
    return out


def _tau(rng):
    r = rng.random()
    if r < 0.04: return 0
    if r < 0.08: return 1000
    return rng.randrange(300, 901, 25)


def _pairs(rng, n):
    """Accepted merge edges (u < v < n, repeats possible) as a matcher at some threshold would produce them."""
    tau = rng.randrange(450, 800, 50)
    return [(u, v) for u, v, s in _cands(rng, n) if s >= tau]


def _ok_tris(ts, n=None, strict=True):
    return all(0 <= s <= 1000 and (u < v if strict else u != v) and (n is None or max(u, v) < n) for u, v, s in ts)


def _ok_pairs(ps, n):
    return all(u < v < n for u, v in ps)


def _ok_tau(t): return 0 <= t <= 1000


# ================================================================ DECIDE
TRI_IN = ("cands is a list of candidate triples (u, v, score): u, v are node ids with u < v, score an integer 0..1000 "
          "(per-mille match confidence); the same pair may occur more than once. ")
ORDER = "descending score, ties broken by ascending u, then ascending v"

DE_TAU = [(500, []), (0, [(0, 1, 0)]), (1000, [(0, 1, 999), (1, 2, 1000)]), (500, [(0, 1, 500), (0, 2, 499), (1, 2, 501)]),
          (600, [(2, 3, 700), (0, 1, 700), (2, 3, 650), (0, 1, 700), (1, 3, 100)]), (1000, [(0, 1, 1000), (0, 1, 1000)])]

program("t5_decide_filter", "T5",
        "Input is (tau, cands): tau is an integer threshold 0..1000 and " + TRI_IN +
        "Output the triples with score >= tau, unchanged and in their original input order (repeats kept). "
        "Empty cands gives [].",
        tup(u24, TRIS), TRIS, lambda a: [t for t in a[1] if t[2] >= a[0]],
        lambda r, n: (_tau(r), _cands(r, n)), S, TS, edges=DE_TAU,
        pre=lambda a: _ok_tau(a[0]) and _ok_tris(a[1]))

program("t5_decide_count", "T5",
        "Input is (tau, cands): tau is an integer threshold 0..1000 and " + TRI_IN +
        "Output the number of triples with score >= tau (every occurrence of a repeated pair counts). Empty cands gives 0.",
        tup(u24, TRIS), u24, lambda a: sum(1 for t in a[1] if t[2] >= a[0]),
        lambda r, n: (_tau(r), _cands(r, n)), S, TS, edges=DE_TAU,
        pre=lambda a: _ok_tau(a[0]) and _ok_tris(a[1]))


def _normalise(ts):
    best = {}
    for u, v, s in ts:
        k = (min(u, v), max(u, v))
        if k not in best or s > best[k]: best[k] = s   # strict >: ties keep the first occurrence
    return [(u, v, best[(u, v)]) for u, v in sorted(best)]

program("t5_decide_normalise", "T5",
        "Input is cands, a list of candidate triples (u, v, score) with u != v and score an integer 0..1000; a pair may appear "
        "in either orientation (u < v or u > v) and more than once. Normalise each triple's pair to (min(u, v), max(u, v)). "
        "Collapse all triples with the same normalised pair into one triple carrying the highest score among them (ties: the "
        "first occurrence in input order is kept, which has the same score, so the output is unaffected). Output one triple "
        "(u, v, score) per distinct normalised pair, with u < v, sorted by ascending u, then ascending v. Empty input gives [].",
        TRIS, TRIS, _normalise, lambda r, n: _cands(r, n, rev=True), S, TS,
        edges=[[], [(3, 1, 40)], [(1, 3, 40), (3, 1, 90), (1, 3, 60)], [(2, 0, 5), (0, 2, 5), (0, 1, 7)],
               [(5, 4, 0), (4, 5, 1000), (0, 9, 300), (9, 0, 300)]],
        pre=lambda ts: _ok_tris(ts, strict=False))


def _drop_known(a):
    known = set(a[0])
    return [t for t in a[1] if (t[0], t[1]) not in known]

def _gen_known(r, n):
    cs = _cands(r, n)
    known = [(u, v) for u, v, _ in cs if r.random() < 0.3]
    if n >= 2:
        for _ in range(r.randint(0, n // 2 + 1)):
            u, v = sorted(r.sample(range(n), 2)); known.append((u, v))
    r.shuffle(known)
    return known, cs

program("t5_decide_drop_known", "T5",
        "Input is (known, cands): known is a list of already existing SAME_AS pairs (a, b) with a < b (any order, repeats "
        "possible) and " + TRI_IN +
        "Output the triples of cands whose pair (u, v) is not equal to any known pair (exact match of both ids, (u, v) == "
        "(a, b); only direct pairs count, not pairs implied transitively), unchanged and in original order, repeats kept. "
        "No score threshold is applied.",
        tup(PAIRS, TRIS), TRIS, _drop_known, _gen_known, S, TS,
        edges=[([], []), ([(0, 1)], []), ([], [(0, 1, 9)]), ([(0, 1)], [(0, 1, 900), (1, 2, 800), (0, 1, 100)]),
               ([(0, 1), (1, 2)], [(0, 2, 999), (1, 2, 5)]), ([(2, 3), (2, 3)], [(0, 3, 1), (2, 3, 2), (0, 2, 3)])],
        pre=lambda a: all(x < y for x, y in a[0]) and _ok_tris(a[1]))

program("t5_decide_order", "T5",
        "Input is (tau, cands): tau is an integer threshold 0..1000 and " + TRI_IN +
        "Keep the triples with score >= tau and output them sorted by " + ORDER + ". Every accepted triple appears, "
        "including repeats of a pair (identical triples appear adjacent, as many times as they occur). Empty result gives [].",
        tup(u24, TRIS), TRIS, lambda a: sorted([t for t in a[1] if t[2] >= a[0]], key=_order_key),
        lambda r, n: (_tau(r), _cands(r, n)), S, TS,
        edges=DE_TAU + [(0, [(3, 4, 5), (0, 9, 5), (0, 2, 5), (1, 2, 6)])],
        pre=lambda a: _ok_tau(a[0]) and _ok_tris(a[1]))

program("t5_decide_top_k", "T5",
        "Input is (k, cands): k >= 0 and " + TRI_IN +
        "Sort all triples (no threshold) by " + ORDER + " (repeats kept, identical triples adjacent). Output the first k "
        "triples of that order, or all of them if there are fewer than k. k = 0 gives [].",
        tup(u24, TRIS), TRIS, lambda a: sorted(a[1], key=_order_key)[:a[0]],
        lambda r, n: (r.randint(0, n + 3), _cands(r, n)), S, TS,
        edges=[(0, []), (3, []), (0, [(0, 1, 5)]), (1, [(0, 2, 5), (0, 1, 5)]), (2, [(1, 2, 3), (0, 1, 3), (0, 2, 9)]),
               (9, [(0, 1, 1), (0, 1, 1), (0, 1, 2)])],
        pre=lambda a: _ok_tris(a[1]))


def _stage_cap(a):
    tau, cap, ts = a
    acc = sorted([t for t in ts if t[2] >= tau], key=_order_key)
    return [(u, v) for u, v, _ in acc[:cap]], max(0, len(acc) - cap)

program("t5_decide_stage_cap", "T5",
        "Input is (tau, cap, cands): tau is an integer threshold 0..1000, cap >= 0 the maximum number of pairs staged per "
        "run, and " + TRI_IN +
        "The accepted triples (score >= tau) are put in processing order: " + ORDER + " (repeats kept, each occurrence "
        "is its own item). The first cap accepted triples in that order are staged; the remaining accepted ones are "
        "deferred. Output (staged, deferred): staged is the list of the staged pairs (u, v) (scores dropped) in processing "
        "order, deferred the number of accepted triples not staged (0 if at most cap are accepted).",
        tup(u24, u24, TRIS), tup(PAIRS, u24), _stage_cap,
        lambda r, n: (_tau(r), r.randint(0, n + 2), _cands(r, n)), S, TS,
        edges=[(500, 3, []), (500, 0, [(0, 1, 600)]), (500, 5, [(0, 1, 600), (1, 2, 400)]),
               (100, 2, [(1, 2, 300), (0, 3, 300), (0, 2, 300), (0, 1, 50)]), (0, 1, [(0, 1, 0), (0, 1, 0)]),
               (700, 2, [(2, 3, 800), (0, 1, 900), (1, 3, 700), (0, 2, 1000)])],
        pre=lambda a: _ok_tau(a[0]) and _ok_tris(a[2]))


def _singleton(a):
    tau, ps = a
    order = sorted(range(6), key=lambda i: (-ps[i], i))
    acc = 0
    for k, i in enumerate(order, 1):
        acc += ps[i]
        if acc >= tau: return order[0] if k == 1 else 6
    return 6

def _gen_probs(r, n):
    tau = r.choice([0, 500, 700, 800, 850, 900, 950, 1000, r.randint(0, 1000)])
    k = r.random()
    if k < 0.15:
        base = r.choice([100, 166, 200, 250])
        ps = [base if r.random() < 0.6 else r.randint(0, base) for _ in range(6)]
        ps[r.randrange(6)] = base
    else:
        p = 1000 - int(r.random() ** 2 * 800); rest = 1000 - p
        cuts = sorted(r.randint(0, rest) for _ in range(4))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [rest])]
        ps = parts[:]; ps.insert(r.randrange(6), p)
        if r.random() < 0.1: ps = [x * r.randint(1, 9) // 10 for x in ps]
    return tau, ps

program("t5_decide_singleton", "T5",
        "Input is (tau, probs): tau is an integer 0..1000 and probs a list of exactly 6 integers 0..1000, the per-mille "
        "probabilities of verbs 0..5 (probs[i] belongs to verb i; the sum is usually 1000 but may be less). Order the verb "
        "indices by descending probability, ties to the lower index first. Take the shortest non-empty prefix of this order "
        "whose probability sum is >= tau (the whole order if no prefix reaches tau): the prediction set. If the prediction "
        "set has exactly one verb, output that verb's index; otherwise output 6 (abstain). Equivalently: if max(probs) >= "
        "tau, output the lowest index i with probs[i] == max(probs), else output 6.",
        tup(u24, L), u24, _singleton, _gen_probs, S, TS,
        edges=[(900, [950, 50, 0, 0, 0, 0]), (900, [500, 500, 0, 0, 0, 0]), (0, [0, 0, 0, 0, 0, 0]),
               (0, [0, 0, 7, 0, 7, 0]), (166, [166, 166, 166, 166, 166, 166]), (1000, [0, 0, 0, 0, 0, 1000]),
               (1000, [0, 0, 0, 0, 0, 999]), (600, [100, 300, 600, 0, 0, 0])],
        pre=lambda a: _ok_tau(a[0]) and len(a[1]) == 6 and all(0 <= p <= 1000 for p in a[1]))


def _stage_idem(a):
    ledger, props = a
    live = {(v, t) for v, t, s in ledger if s in (0, 1)}
    out = []
    for p in props:
        if p in live: continue
        live.add(p); out.append(p)
    return out

def _gen_idem(r, n):
    nt = max(n, 1)
    ledger = [(r.randrange(6), r.randrange(nt), r.randrange(4)) for _ in range(r.randint(0, n + 1))]
    props = []
    for _ in range(r.randint(0, n + 2)):
        x = r.random()
        if x < 0.4 and ledger: props.append(r.choice(ledger)[:2])
        elif x < 0.55 and props: props.append(r.choice(props))
        else: props.append((r.randrange(6), r.randrange(nt)))
    return ledger, props

program("t5_decide_stage_idem", "T5",
        "Input is (ledger, proposals). ledger is a list of existing staging entries (verb, target, status): verb 0..5, "
        "target a node id, status 0 = Staged, 1 = Applied, 2 = Rejected, 3 = Undone; the same (verb, target) may appear "
        "several times with different statuses. proposals is a list of (verb, target). Process the proposals in order. "
        "A proposal is dropped if the ledger has at least one entry with the same verb, the same target and status 0 or 1 "
        "(Rejected and Undone entries never block), or if an identical (verb, target) proposal was already kept earlier in "
        "this list; otherwise it is kept. The same target with a different verb does not block. Output the kept "
        "proposals (verb, target) in their original order.",
        tup(list_of(TRI), PAIRS), PAIRS, _stage_idem, _gen_idem, S, TS,
        edges=[([], []), ([], [(0, 1), (0, 1), (1, 1)]), ([(0, 1, 0)], [(0, 1), (1, 1)]), ([(0, 1, 1)], [(0, 1)]),
               ([(0, 1, 2), (3, 4, 3)], [(0, 1), (3, 4), (3, 4)]), ([(2, 5, 3), (2, 5, 1)], [(2, 5), (2, 6)]),
               ([(5, 0, 0)], [])],
        pre=lambda a: all(v < 6 and s < 4 for v, _, s in a[0]) and all(v < 6 for v, _ in a[1]))


# ================================================================ CLUSTER
CL = ("Input is (n, pairs): n nodes with ids 0..n-1 and pairs, a list of merge edges (u, v) with u < v < n (repeated pairs "
      "may occur). Clusters are the connected components of the undirected graph on nodes 0..n-1 with these edges (the "
      "transitive closure of the merges); a node in no pair is a cluster of size 1. ")
CANON = "The canonical id of a cluster is its largest member id. "

CE = [(0, []), (1, []), (3, []), (2, [(0, 1)]), (4, [(0, 1), (1, 2), (2, 3)]), (5, [(0, 4), (1, 3), (0, 4)]),
      (6, [(0, 5), (1, 5), (2, 5), (3, 4)]), (9, [(i, i + 1) for i in range(8)]), (4, [(2, 3), (0, 1), (1, 2)]),
      (7, [(1, 6), (2, 4), (0, 3), (3, 4)])]
CPRE = lambda a: _ok_pairs(a[1], a[0])
CGEN = lambda r, n: (n, _pairs(r, n))


def _label(a):
    n, ps = a; out = [0] * n
    for c in _clusters(n, ps):
        for i in c: out[i] = c[0]
    return out

program("t5_cluster_label", "T5",
        CL + "Output a list of length n whose entry i is the smallest node id in i's cluster (so a singleton i gets i). "
        "n = 0 gives [].",
        tup(u24, PAIRS), L, _label, CGEN, S, TS, edges=CE, pre=CPRE)


def _canon(a):
    n, ps = a; out = [0] * n
    for c in _clusters(n, ps):
        for i in c: out[i] = c[-1]
    return out

program("t5_cluster_canon", "T5",
        CL + CANON + "Output a list of length n whose entry i is the canonical id (largest node id) of i's cluster (so a "
        "singleton i gets i). n = 0 gives [].",
        tup(u24, PAIRS), L, _canon, CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_count", "T5",
        CL + "Output the number of clusters, singletons included. n = 0 gives 0.",
        tup(u24, PAIRS), u24, lambda a: len(_clusters(*a)), CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_sizes", "T5",
        CL + CANON + "Output the sizes (member counts) of all clusters, singletons included, one entry per cluster, listed "
        "in ascending order of the clusters' canonical ids. The entries sum to n. n = 0 gives [].",
        tup(u24, PAIRS), L, lambda a: [len(c) for c in sorted(_clusters(*a), key=lambda c: c[-1])], CGEN, S, TS,
        edges=CE, pre=CPRE)


def _hist(a):
    h = [0] * 8
    for c in _clusters(*a): h[min(len(c), 8) - 1] += 1
    return h

program("t5_cluster_histogram", "T5",
        CL + "Output a list of exactly 8 counts: for i in 0..6, entry i is the number of clusters with exactly i + 1 "
        "members; entry 7 is the number of clusters with 8 or more members. Singletons count in entry 0. n = 0 gives "
        "[0, 0, 0, 0, 0, 0, 0, 0].",
        tup(u24, PAIRS), L, _hist, CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_largest", "T5",
        CL + "Output the number of members of the largest cluster (1 if there are nodes but no pairs, 0 when n = 0).",
        tup(u24, PAIRS), u24, lambda a: max((len(c) for c in _clusters(*a)), default=0), CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_singletons", "T5",
        CL + "Output the number of clusters with exactly one member (nodes that occur in no pair). n = 0 gives 0.",
        tup(u24, PAIRS), u24, lambda a: sum(1 for c in _clusters(*a) if len(c) == 1), CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_list", "T5",
        CL + "Output all clusters as a list of lists: each cluster is the ascending list of its member ids, and the "
        "clusters are ordered by ascending smallest member (so the first contains node 0). Singletons are included as "
        "one-element lists. n = 0 gives [].",
        tup(u24, PAIRS), list_of(L), lambda a: _clusters(*a), CGEN, S, TS, edges=CE, pre=CPRE)


def _emit(a):
    return sorted((i, c[-1]) for c in _clusters(*a) for i in c[:-1])

program("t5_cluster_emit", "T5",
        CL + CANON + "Output the SAME_AS facts to emit: for every node d that is not the canonical id of its cluster, the "
        "pair (d, c) where c is the canonical id of d's cluster (so d < c). Canonical ids and singletons emit nothing. "
        "The pairs are sorted by ascending d (one pair per d). No pairs gives [].",
        tup(u24, PAIRS), PAIRS, _emit, CGEN, S, TS, edges=CE, pre=CPRE)


def _closure(a):
    return sum(len(c) * (len(c) - 1) // 2 for c in _clusters(*a))

program("t5_cluster_closure_pairs", "T5",
        CL + "Output the number of unordered pairs {a, b} of distinct nodes that lie in the same cluster, i.e. the sum "
        "over clusters of s * (s - 1) / 2 where s is the cluster size. n = 0 gives 0.",
        tup(u24, PAIRS), u24, _closure, CGEN, S, TS, edges=CE, pre=CPRE)

program("t5_cluster_implied_unproposed", "T5",
        CL + "Output the number of unordered node pairs {a, b}, a < b, that lie in the same cluster but do not occur in "
        "the input as a pair (u, v) = (a, b): pairs implied by transitivity but never proposed. This is the sum over "
        "clusters of s * (s - 1) / 2 (s = cluster size) minus the number of distinct pairs in the input (a pair repeated "
        "in the input counts once).",
        tup(u24, PAIRS), u24, lambda a: _closure(a) - len(set(a[1])), CGEN, S, TS, edges=CE, pre=CPRE)

CL_X = ("Input is (n, x, pairs): n >= 1 nodes with ids 0..n-1, a node x < n, and pairs, a list of merge edges (u, v) with "
        "u < v < n (repeated pairs may occur). Clusters are the connected components of the undirected graph on nodes "
        "0..n-1 with these edges (the transitive closure of the merges); a node in no pair is a cluster of size 1. ")
CXE = [(1, 0, []), (3, 2, []), (2, 0, [(0, 1)]), (4, 3, [(0, 1), (1, 2), (2, 3)]), (5, 1, [(0, 4), (1, 3), (0, 4)]),
       (6, 3, [(0, 5), (1, 5), (2, 5), (3, 4)]), (6, 0, [(0, 5), (1, 5), (2, 5), (3, 4)]), (9, 4, [(i, i + 1) for i in range(8)])]
CXPRE = lambda a: a[1] < a[0] and _ok_pairs(a[2], a[0])

def _gen_x(r, n):
    n = max(n, 1)
    return n, r.randrange(n), _pairs(r, n)

def _members(a):
    n, x, ps = a
    return next(c for c in _clusters(n, ps) if x in c)

program("t5_cluster_members_of", "T5",
        CL_X + "Output the ascending list of the member ids of x's cluster (it always contains x; a singleton gives [x]).",
        tup(u24, u24, PAIRS), L, _members, _gen_x, S, TS, edges=CXE, pre=CXPRE)

program("t5_cluster_canon_of", "T5",
        CL_X + "Output the canonical id of x's cluster: its largest member id (x itself if x is a singleton or the largest).",
        tup(u24, u24, PAIRS), u24, lambda a: _members(a)[-1], _gen_x, S, TS, edges=CXE, pre=CXPRE)


def _same(a):
    n, ps, qs = a
    root = _roots(n, ps)
    return [int(root[x] == root[y]) for x, y in qs]

def _gen_same(r, n):
    ps = _pairs(r, n)
    qs = []
    if n:
        for _ in range(r.randint(0, n + 2)):
            if ps and r.random() < 0.4:
                u, v = r.choice(ps); w = r.choice(ps)[r.randrange(2)]
                qs.append((u, w) if r.random() < 0.5 else (w, v))
            else:
                qs.append((r.randrange(n), r.randrange(n)))
    return n, ps, qs

program("t5_cluster_same", "T5",
        "Input is (n, pairs, queries): n nodes with ids 0..n-1; pairs, a list of merge edges (u, v) with u < v < n "
        "(repeated pairs may occur); queries, a list of (a, b) with a, b < n in either order (a may equal b). Clusters are "
        "the connected components of the undirected graph on nodes 0..n-1 with the merge edges (transitive closure); a node "
        "in no pair is a cluster of size 1. Output one entry per query, in query order: 1 if a and b are in the same "
        "cluster, else 0 (a == b always gives 1). No queries gives [].",
        tup(u24, PAIRS, PAIRS), L, _same, _gen_same, S, TS,
        edges=[(0, [], []), (1, [], [(0, 0)]), (3, [(0, 1)], [(0, 1), (1, 0), (0, 2), (2, 2)]),
               (4, [(0, 1), (2, 3), (1, 2)], [(0, 3), (3, 0)]), (5, [(0, 4), (1, 3)], [(0, 1), (4, 0), (3, 1), (2, 4)])],
        pre=lambda a: _ok_pairs(a[1], a[0]) and all(x < a[0] and y < a[0] for x, y in a[2]))


def _merge_count(a):
    n, tau, ts = a
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    k = 0
    for u, v, _ in sorted([t for t in ts if t[2] >= tau], key=_order_key):
        a_, b_ = find(u), find(v)
        if a_ != b_: parent[a_] = b_; k += 1
    return k

program("t5_cluster_merge_count", "T5",
        "Input is (n, tau, cands): n nodes with ids 0..n-1, tau an integer threshold 0..1000, and cands a list of candidate "
        "triples (u, v, score) with u < v < n and score an integer 0..1000 (the same pair may occur more than once). The "
        "accepted triples are those with score >= tau. Start from n singleton clusters and process the accepted triples one "
        "at a time in the order " + ORDER + "; each merges the clusters of u and v. Output the number of accepted triples "
        "whose u and v were in different clusters at the moment they were processed (merges that actually joined two "
        "clusters; a triple whose ends are already connected, including a repeat of an earlier pair, is not counted).",
        tup(u24, u24, TRIS), u24, _merge_count, lambda r, n: (n, _tau(r), _cands(r, n)), S, TS,
        edges=[(0, 500, []), (3, 500, []), (2, 500, [(0, 1, 499)]), (2, 500, [(0, 1, 500), (0, 1, 900)]),
               (3, 0, [(0, 1, 5), (1, 2, 6), (0, 2, 7)]), (5, 600, [(0, 1, 700), (2, 3, 800), (1, 3, 600), (0, 2, 650), (3, 4, 10)])],
        pre=lambda a: _ok_tau(a[1]) and _ok_tris(a[2], a[0]))


def _gen_ge(r, n):
    return n, r.choice([0, 1, 2, 2, 3, 3, 4, 5, 8]), _pairs(r, n)

program("t5_cluster_count_ge", "T5",
        "Input is (n, k, pairs): n nodes with ids 0..n-1, a size bound k >= 0, and pairs, a list of merge edges (u, v) with "
        "u < v < n (repeated pairs may occur). Clusters are the connected components of the undirected graph on nodes "
        "0..n-1 with these edges (transitive closure); a node in no pair is a cluster of size 1. Output the number of "
        "clusters with at least k members, singletons included when k <= 1 (k = 0 or 1 gives the total number of "
        "clusters). n = 0 gives 0.",
        tup(u24, u24, PAIRS), u24, lambda a: sum(1 for c in _clusters(a[0], a[2]) if len(c) >= a[1]), _gen_ge, S, TS,
        edges=[(0, 0, []), (3, 0, []), (3, 2, []), (4, 2, [(0, 1)]), (4, 4, [(0, 1), (1, 2), (2, 3)]),
               (6, 3, [(0, 5), (1, 5), (3, 4)]), (9, 9, [(i, i + 1) for i in range(8)]), (5, 7, [(0, 1)])],
        pre=lambda a: _ok_pairs(a[2], a[0]))
