"""Unit tests for genome/lib/recipes.py. Each recipe is wrapped in a small glue program and checked by the unmodified
genome.verify.verify (edge cases + random + large sizes + exhaustive small sweep) against a Python reference.
Several wrappers are real corpus programs that are NOT in the exp20 held-out set (t5_decide_filter, t5_decide_count,
t3_cc_label, t3_sp_count, t5_rewrite_sameas_roots).
usage: python3 -m genome.lib.test_recipes [name ...]   (prints PASS/FAIL, depth and interactions per recipe)"""
import sys, random
from collections import Counter, deque
from genome.corpus import Program as CP, load_all
from genome.types import u24, list_of, tup
from genome.verify import verify
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, WEDGE, INF
from genome.lib import recipes as R

L_ = list_of(u24)
PAIRS = list_of(tup(u24, u24))
TRIS = list_of(tup(u24, u24, u24))
M = 0xFFFFFF


def cp(id, desc, inp, out, ref, gen, edges, pre=None, sizes=(0, 1, 2, 3, 5, 8), test=(64, 128)):
    return CP(id, "T", desc, inp, out, ref, gen, list(sizes), list(test), edges, pre)


def rlist(r, n, hi): return [r.randrange(hi) for _ in range(n)]


def graph(r, n, directed):
    es = set()
    for _ in range(int(n * 1.5)):
        if n < 2: break
        u, v = r.randrange(n), r.randrange(n)
        if u == v: continue
        if not directed and ((v, u) in es): continue
        es.add((u, v))
    es = list(es); r.shuffle(es)
    return es


TESTS = {}


def test(f):
    TESTS[f.__name__] = f
    return f


# ------------------------------------------------------------------ list recipes
@test
def list_length_and_copy():
    P = Program()
    lc = R.list_length_and_copy(P, "lc", NUM, copies=2, key=lambda d, x: x)
    cw = R.count_where(P, "cw", NUM, lambda d, x: 1)
    def prog(d, xs):
        n, mx, c1, c2 = d.call(lc, list=xs)
        d.erase(d.call(cw, list=c2))
        return (n, mx, c1)
    P.prog(prog, inputs=[("xs", LIST(NUM))], out=TUP(NUM, NUM, LIST(NUM)))
    return P, cp("r_len", "", L_, tup(u24, u24, L_), lambda xs: (len(xs), max(xs, default=0), xs),
                 lambda r, n: rlist(r, n, 1000), [[], [0], [7, 3, 9]])


@test
def list_to_trie_lookup_many():
    P = Program()
    lc = R.list_length_and_copy(P, "lc", NUM)
    lt = R.list_to_trie(P, "lt", NUM)
    lk = R.lookup_many(P, "lk", NUM, lambda d, k: k)
    def prog(d, inp):
        vals, keys = inp[0], inp[1]
        n, c = d.call(lc, list=vals)
        L1, L2 = d.fanout(R.depth_for(P, d, n), 2)
        V = d.call(lt, list=c, L=L1)
        return d.call(lk, list=keys, V=V, L=L2)
    def prog2(d, vals, keys): return prog(d, (vals, keys))
    P.prog(prog2, inputs=[("vals", LIST(NUM)), ("keys", LIST(NUM))], out=LIST(TUP(NUM, NUM)))
    def gen(r, n):
        v = rlist(r, n, 500)
        return (v, rlist(r, 2 * n, n) if n else [])
    return P, cp("r_lookup", "", tup(L_, L_), PAIRS, lambda a: [(k, a[0][k]) for k in a[1]], gen,
                 [([], []), ([5], [0, 0]), ([1, 2, 3], [2, 0, 1, 2])], pre=lambda a: all(k < len(a[0]) for k in a[1]))


@test
def filter_in_order():
    P = Program()
    f = R.filter_in_order(P, "keep", WEDGE, lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)
    P.prog("t5_decide_filter", lambda d, tau, cands: d.call(f, list=cands, E=tau))
    return P, load_all()["t5_decide_filter"]


@test
def count_where():
    P = Program()
    f = R.count_where(P, "cnt", WEDGE, lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)
    P.prog("t5_decide_count", lambda d, tau, cands: d.call(f, list=cands, E=tau))
    return P, load_all()["t5_decide_count"]


@test
def take_first():
    P = Program()
    t = R.take_first(P, "tk", EDGE)
    def prog(d, k, xs):
        o, rest = d.call(t, list=xs, k=k)
        return (o, rest)
    P.prog(prog, inputs=[("k", NUM), ("xs", LIST(EDGE))], out=TUP(LIST(EDGE), NUM))
    return P, cp("r_take", "", tup(u24, PAIRS), tup(PAIRS, u24), lambda a: (a[1][:a[0]], max(0, len(a[1]) - a[0])),
                 lambda r, n: (r.randrange(n + 2), [(r.randrange(9), r.randrange(9)) for _ in range(n)]),
                 [(0, []), (0, [(1, 2)]), (5, [(1, 2)]), (1, [(1, 2), (3, 4)])])


@test
def argmax_first():
    P = Program()
    a = R.argmax_first(P, "am", NUM, lambda d, x: x)
    def prog(d, xs):
        m, i = d.call(a, list=xs)
        return (m, i)
    P.prog(prog, inputs=[("xs", LIST(NUM))], out=TUP(NUM, NUM))
    ref = lambda xs: (max(xs), xs.index(max(xs))) if xs else (0, INF)
    return P, cp("r_argmax", "", L_, tup(u24, u24), ref, lambda r, n: rlist(r, n, 6), [[], [0], [0, 0], [3, 5, 5, 1]])


@test
def sort_by():
    P = Program()
    s = R.sort_by(P, "srt", WEDGE, lambda d, u, v, s: (d.op(1000, "-", s), u, v))
    P.prog(lambda d, xs: d.call(s, list=xs), inputs=[("xs", LIST(WEDGE))], out=LIST(WEDGE))
    ref = lambda xs: sorted(xs, key=lambda t: (-t[2], t[0], t[1]))
    gen = lambda r, n: [(r.randrange(5), r.randrange(5), r.choice([0, 1, 500, 999, 1000])) for _ in range(n)]
    return P, cp("r_sort", "", TRIS, TRIS, ref, gen, [[], [(0, 1, 5)], [(1, 2, 3), (0, 1, 3), (0, 1, 3), (4, 5, 1000)]],
                 pre=lambda xs: all(t[2] <= 1000 for t in xs), test=(48, 96))


@test
def sort_by_single_key():
    P = Program()
    s = R.sort_by(P, "srt", NUM, lambda d, x: x)
    P.prog(lambda d, xs: d.call(s, list=xs), inputs=[("xs", LIST(NUM))], out=LIST(NUM))
    return P, cp("r_sort1", "", L_, L_, sorted, lambda r, n: rlist(r, n, 20), [[], [3], [2, 1, 2, 0]], test=(48, 96))


# ------------------------------------------------------------------ keyed / trie recipes
@test
def reduce_by_key_and_select_sorted():
    """distinct sorted pairs: pack (u, v) -> reduce_by_key set1 -> select_sorted occupied leaves -> unpack."""
    P = Program()
    lc = R.list_length_and_copy(P, "lc", EDGE, key=lambda d, u, v: R.max2(d, u, v))
    rk = R.reduce_by_key(P, "rk", EDGE, lambda d, u, v, B: R.pack(d, u, v, B), "set1", env=NUM)
    sel = R.select_sorted(P, "sel", lambda d, x, i, B: x, lambda d, x, i, B: R.unpack(d, i, B))
    def prog(d, es):
        n, mx, c = d.call(lc, list=es)
        d.erase(n)
        B1, B2, B3, B4 = d.fanout(R.depth_for(P, d, d.op(mx, "+", 1)), 4)
        L1, L2 = d.fanout(d.as_depth(d.op(B1, "*", 2)), 2)
        H = d.call(rk, list=c, L=L1, E=B2)
        d.erase(B3)
        return d.call(sel, t=H, L=L2, E=B4)
    P.prog(prog, inputs=[("es", LIST(EDGE))], out=LIST(EDGE))
    return P, cp("r_dedup", "", PAIRS, PAIRS, lambda es: sorted(set(es)),
                 lambda r, n: [(r.randrange(n + 1), r.randrange(n + 1)) for _ in range(2 * n)],
                 [[], [(0, 0)], [(3, 1), (0, 2), (3, 1)]], test=(40, 64))


@test
def reduce_by_key_min_argmax_trie():
    """(n, [(k, v)]) with k < n: per-key min (INF if none) as a list, plus argmax over the per-key counts."""
    P = Program()
    lc = R.list_length_and_copy(P, "lc", EDGE, copies=2)
    mn = R.reduce_by_key(P, "mn", EDGE, lambda d, k, v: (k, v), "min")
    ct = R.reduce_by_key(P, "ct", EDGE, lambda d, k, v: k, "inc")
    am = R.argmax_first_trie(P, "am", lambda d, x, i, n: (d.op(i, "<", n), x))
    tl = P.to_list("tl")
    def prog(d, n, kv):
        m, c1, c2 = d.call(lc, list=kv)
        d.erase(m)
        n1, n2 = d.fanout(n, 2)
        L1, L2, L3, L4 = d.fanout(R.depth_for(P, d, n1), 4)
        H = d.call(mn, list=c1, L=L1)
        C = d.call(ct, list=c2, L=L2)
        n3, n4 = d.fanout(n2, 2)
        mx, ix = d.call(am, t=C, L=L3, E=n3)
        return (d.call(tl, t=H, L=L4, n=n4), mx, ix)
    P.prog(prog, inputs=[("n", NUM), ("kv", LIST(EDGE))], out=TUP(LIST(NUM), NUM, NUM))
    def ref(a):
        n, kv = a
        mins = [min([v for k, v in kv if k == i], default=INF) for i in range(n)]
        cnt = [sum(1 for k, _ in kv if k == i) for i in range(n)]
        return (mins, max(cnt), cnt.index(max(cnt))) if n else ([], 0, INF)
    gen = lambda r, n: (n, [(r.randrange(n), r.randrange(50)) for _ in range(2 * n)] if n else [])
    return P, cp("r_rbk", "", tup(u24, PAIRS), tup(L_, u24, u24), ref, gen,
                 [(0, []), (1, []), (2, [(1, 0)]), (3, [(2, 5), (0, 1), (2, 3)])], pre=lambda a: all(k < a[0] for k, _ in a[1]))


@test
def count_where_trie():
    """number of distinct values."""
    P = Program()
    lc = R.list_length_and_copy(P, "lc", NUM, key=lambda d, x: x)
    rk = R.reduce_by_key(P, "rk", NUM, lambda d, x: x, "set1")
    cw = R.count_where_trie(P, "cw", lambda d, x, i, E: x)
    def prog(d, xs):
        n, mx, c = d.call(lc, list=xs)
        d.erase(n)
        L1, L2 = d.fanout(R.depth_for(P, d, d.op(mx, "+", 1)), 2)
        return d.call(cw, t=d.call(rk, list=c, L=L1), L=L2, E=0)
    P.prog(prog, inputs=[("xs", LIST(NUM))], out=NUM)
    return P, cp("r_distinct", "", L_, u24, lambda xs: len(set(xs)), lambda r, n: rlist(r, n, 3 * n + 1), [[], [0], [5, 5, 1]])


# ------------------------------------------------------------------ graph recipes
@test
def frontier_relax_min():
    P = Program()
    lg = P.lg(); adj = P.adjacency(); ea = P.empty_adj()
    infs = P.const_trie("infs", INF); io = P.iota_trie("io"); tl = P.to_list("tl")
    fr = R.frontier_relax(P, "cc", "min")          # msg m + w with w = 0: min-label propagation
    def step(d, L, g, u, v):
        L1, L2, L3 = d.fanout(L, 3); u1, u2 = d.fanout(u, 2); v1, v2 = d.fanout(v, 2)
        g = d.call(adj, G=g, u=u1, L=L1, v=v1, w=0)
        return L3, d.call(adj, G=g, u=v2, L=L2, v=u2, w=0)
    def fin(d, L, g): d.erase(L); return g
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", TRIE(LIST(TUP(NUM, NUM))))], elem=EDGE)
    def prog(d, n, es):
        def empty(b, es): b.erase(es); return b.nil()
        def ne(b, nm1, es):
            a, c = b.fanout(nm1, 2)
            L = b.call(lg, x=a); L1, L2, L3, L4, L5, L6 = b.fanout(L, 6)
            G = b.call(w, list=es, init=(L1, b.call(ea, L=L2)))
            D = b.call(fr, G=G, D=b.call(infs, L=L3), C=b.call(io, L=L4), L=L5)
            return b.call(tl, t=D, L=L6, n=b.op(c, "+", 1))
        return d.branch(n, empty, ne, es)
    P.prog("t3_cc_label", prog)
    return P, load_all()["t3_cc_label"]


@test
def frontier_relax_or():
    """directed reachability as 0/1 list with combine "or"."""
    P = Program()
    lg = P.lg(); adj = P.adjacency(); ea = P.empty_adj()
    z = P.const_trie("z", 0); seed = P.update("seed", "set1"); tl = P.to_list("tl")
    fr = R.frontier_relax(P, "rc", "or")
    def step(d, L, g, u, v):
        L1, L2 = d.fanout(L, 2)
        return L2, d.call(adj, G=g, u=u, L=L1, v=v, w=1)
    def fin(d, L, g): d.erase(L); return g
    w = P.stream("w", step, fin, state=[("L", DEPTH), ("g", TRIE(LIST(TUP(NUM, NUM))))], elem=EDGE)
    def prog(d, n, s, es):
        n1, n2 = d.fanout(n, 2)
        L = R.depth_for(P, d, n1); L1, L2, L3, L4, L5, L6, L7 = d.fanout(L, 7)
        G = d.call(w, list=es, init=(L1, d.call(ea, L=L2)))
        C = d.call(seed, t=d.call(z, L=L3), k=s, L=L4)
        D = d.call(fr, G=G, D=d.call(z, L=L5), C=C, L=L6)
        return d.call(tl, t=D, L=L7, n=n2)
    P.prog(prog, inputs=[("n", NUM), ("s", NUM), ("es", LIST(EDGE))], out=LIST(NUM))
    def ref(a):
        n, s, es = a
        seen = {s}; q = [s]
        while q:
            u = q.pop()
            for x, y in es:
                if x == u and y not in seen: seen.add(y); q.append(y)
        return [int(i in seen) for i in range(n)]
    gen = lambda r, n: (max(n, 1), r.randrange(max(n, 1)), graph(r, max(n, 1), True))
    return P, cp("r_reach", "", tup(u24, u24, PAIRS), L_, ref, gen, [(1, 0, []), (2, 1, [(0, 1)]), (3, 0, [(0, 1), (1, 2)])],
                 pre=lambda a: a[0] >= 1 and a[1] < a[0] and all(u < a[0] and v < a[0] and u != v for u, v in a[2])
                 and len(set(a[2])) == len(a[2]))


@test
def layered_bfs_count_directed():
    P = Program()
    lb = R.layered_bfs_count(P, "lb", directed=True)
    gt = P.get("gt")
    def prog(d, n, s, t, es):
        n1, n2 = d.fanout(n, 2)
        L1, L2 = d.fanout(R.depth_for(P, d, n1), 2)
        D, C = d.call(lb, n=n2, s=s, es=es, L=L1)
        d.erase(D)
        return d.call(gt, t=C, k=t, L=L2)
    P.prog("t3_sp_count", prog)
    return P, load_all()["t3_sp_count"]


@test
def layered_bfs_count_undirected():
    P = Program()
    lb = R.layered_bfs_count(P, "lb", directed=False)
    tl = P.to_list("tl")
    def prog(d, n, s, es):
        n1, n2, n3, n4 = d.fanout(n, 4)
        L1, L2, L3 = d.fanout(R.depth_for(P, d, n1), 3)
        D, C = d.call(lb, n=n2, s=s, es=es, L=L1)
        return (d.call(tl, t=D, L=L2, n=n3), d.call(tl, t=C, L=L3, n=n4))
    P.prog(prog, inputs=[("n", NUM), ("s", NUM), ("es", LIST(EDGE))], out=TUP(LIST(NUM), LIST(NUM)))
    def ref(a):
        n, s, es = a
        adj = [[] for _ in range(n)]
        for u, v in es: adj[u].append(v); adj[v].append(u)
        D = [INF] * n; C = [0] * n; D[s] = 0; C[s] = 1; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if D[v] == INF: D[v] = D[u] + 1; q.append(v)
                if D[v] == D[u] + 1: C[v] = (C[v] + C[u]) & M
        return (D, C)
    gen = lambda r, n: (max(n, 1), r.randrange(max(n, 1)), graph(r, max(n, 1), False))
    pre = lambda a: (a[0] >= 1 and a[1] < a[0] and all(u < a[0] and v < a[0] and u != v for u, v in a[2])
                     and len({frozenset(e) for e in a[2]}) == len(a[2]))
    return P, cp("r_bfscount", "", tup(u24, u24, PAIRS), tup(L_, L_), ref, gen,
                 [(1, 0, []), (2, 0, [(1, 0)]), (4, 0, [(0, 1), (0, 2), (1, 3), (2, 3)])], pre=pre)


@test
def pointer_jump():
    P = Program()
    pj = R.pointer_jump(P, "pj")
    P.prog("t5_rewrite_sameas_roots", lambda d, p: d.call(pj, list=p))
    return P, load_all()["t5_rewrite_sameas_roots"]


def run(names=None, seed=0, workers=2, quiet=False):
    res = {}
    for nm, f in TESTS.items():
        if names and nm not in names: continue
        try:
            P, prog = f()
            book = P.build()
        except Exception as e:
            print(f"FAIL  {nm:34s} build error: {type(e).__name__}: {e}"); res[nm] = {"status": "build-error", "err": str(e)}
            continue
        r = verify(prog, book, seed, 60.0, workers)
        m = r.get("metrics", {})
        print(f"{'PASS' if r['status'] == 'pass' else 'FAIL'}  {nm:34s} {prog.id:26s} cases {r.get('cases')}  "
              f"depth(big) {m.get('depth_median_big')}  itrs(big) {m.get('itrs_median_big')}", flush=True)
        if r["status"] != "pass": print("   ", r.get("counterexample") or r.get("reason"))
        res[nm] = {"status": r["status"], "metrics": m, "prog": prog.id, "cx": r.get("counterexample")}
    return res


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    out = run(args or None)
    print(f"{sum(v['status'] == 'pass' for v in out.values())}/{len(out)} pass")
