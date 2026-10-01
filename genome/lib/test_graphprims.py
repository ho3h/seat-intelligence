"""Unit tests for genome/lib/graphprims.py: each primitive is wrapped in a tiny @prog and run by the pinned executor
against a Python model on random and edge inputs.  usage: python3 -m genome.lib.test_graphprims [-v]"""
import random, sys, heapq
from concurrent.futures import ThreadPoolExecutor
from genome.types import encode, decode, u24, list_of, tup
from genome.executor import run_net
from genome.lib import graphprims as G

INF = G.INF
L_ = list_of(u24)
PAIRS = list_of(tup(u24, u24))
TRIS = list_of(tup(u24, u24, u24))
lgp = lambda x: x.bit_length()
VERB = "-v" in sys.argv


def run(book: G.Book, it, ot, v, depth=False):
    root, defs = encode(v, it)
    src = f"@main = r\n  & @prog ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + book.text()
    r = run_net(src, "depth" if depth else "run", 60)
    if not r.ok: return ("ERROR", r.error[:300]), r
    try: return decode(r.result, ot), r
    except Exception as e: return ("DECODE", str(e)[:200], r.result[:200]), r


def check(name, book, it, ot, cases, ref):
    from genome.verify import lint_net
    lint = lint_net(book.text())
    if lint:
        print(f"FAIL  {name:28s} static check: {lint[:300]}"); return False
    def one(v):
        got, r = run(book, it, ot, v)
        return v, got, ref(v), r
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(one, cases))
    bad = [(v, g, e) for v, g, e, _ in res if g != e]
    big = max(res, key=lambda x: len(repr(x[0])))
    _, r = run(book, it, ot, big[0], depth=True)
    print(f"{'PASS' if not bad else 'FAIL'}  {name:28s} {len(cases)-len(bad)}/{len(cases)}   largest case: "
          f"depth {r.depth}, itrs {r.itrs}")
    for v, g, e in bad[:2]: print("   input", repr(v)[:200], "\n   got  ", repr(g)[:200], "\n   want ", repr(e)[:200])
    return not bad


def pairs_updates(n, act):
    """Program: input (n, [(k, p)]) with n >= 1; apply the keyed updates in list order to a const trie and output
    the first n leaves.  Composes lg + const_trie + stream + update + to_list."""
    init = {"min": str(INF), "push": "(0 *)"}.get(act, "0")
    b = G.Book(); G.lg(b); G.const_trie(b, "z", init); G.update(b, "up", act); G.to_list(b, "tl")
    G.stream(b, "w", 4, "((L t) ((k p) (L3 t2)))\n  & L ~ {L1 L3}\n  & @up ~ (t (k (L1 (p t2))))", "((* t) t)")
    b.add("""
@prog = ((n ups) out)
  & n ~ {n1 n2}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 L3}}
  & @z ~ (L1 t0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @tl ~ (t (L3 (0 (n2 ((0 *) out)))))
""")
    return b


def py_updates(act):
    def f(v):
        n, ups = v
        t = {"min": [INF] * n, "push": [[] for _ in range(n)]}.get(act, [0] * n)
        for k, p in ups:
            if act == "set1": t[k] = 1
            elif act == "set": t[k] = p
            elif act == "inc": t[k] += 1
            elif act == "add": t[k] = (t[k] + p) & INF
            elif act == "or": t[k] |= p
            elif act == "min": t[k] = min(t[k], p)
            elif act == "max": t[k] = max(t[k], p)
            elif act == "push": t[k] = [p] + t[k]
        return t
    return f


def gen_ups(rng, cnt=30):
    out = [(1, [])]
    for _ in range(cnt):
        n = rng.choice([1, 2, 3, 5, 8, 13, 40, 100])
        out.append((n, [(rng.randrange(n), rng.randrange(1000)) for _ in range(rng.randrange(3 * n + 1))]))
    return out


def main():
    rng = random.Random(8)
    ok = True
    # --- lg
    b = G.Book(); G.lg(b); b.add("@prog = (x o)\n  & @lg ~ (x o)")
    ok &= check("lg", b, u24, u24, list(range(0, 40)) + [255, 256, 1000, INF], lgp)
    # --- const_trie + to_list (to_list is fold)
    b = G.Book(); G.lg(b); G.const_trie(b, "z7", "7"); G.to_list(b, "tl")
    b.add("@prog = (n out)\n  & n ~ {n1 n2}\n  & n1 ~ $([-] $(1 m))\n  & @lg ~ (m L)\n  & L ~ {L1 L2}\n"
          "  & @z7 ~ (L1 t)\n  & @tl ~ (t (L2 (0 (n2 ((0 *) out)))))")
    ok &= check("const_trie+to_list", b, u24, L_, list(range(1, 20)) + [100, 257], lambda n: [7] * n)
    # --- iota_trie
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.to_list(b, "tl")
    b.add("@prog = ((n base) out)\n  & n ~ {n1 n2}\n  & n1 ~ $([-] $(1 m))\n  & @lg ~ (m L)\n  & L ~ {L1 L2}\n"
          "  & @io ~ (L1 (base t))\n  & @tl ~ (t (L2 (0 (n2 ((0 *) out)))))")
    ok &= check("iota_trie", b, tup(u24, u24), L_, [(n, rng.randrange(100)) for n in list(range(1, 12)) + [64, 100]],
                lambda v: [v[1] + i for i in range(v[0])])
    # --- update with every act (+ stream walker)
    cases = gen_ups(rng)
    for act in ["set1", "set", "inc", "add", "or", "min", "max", "push"]:
        ot = list_of(L_) if act == "push" else L_
        ok &= check(f"update[{act}]+stream", pairs_updates(1, act), tup(u24, PAIRS), ot, cases, py_updates(act))
    # --- get
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.get(b, "g")
    b.add("@prog = ((n k) out)\n  & n ~ $([-] $(1 m))\n  & @lg ~ (m L)\n  & L ~ {L1 L2}\n"
          "  & @io ~ (L1 (100 t))\n  & @g ~ (t (k (L2 out)))")
    cs = [(n, rng.randrange(n)) for n in [1, 2, 3, 7, 8, 9, 50, 200] for _ in range(3)]
    ok &= check("get", b, tup(u24, u24), u24, cs, lambda v: 100 + v[1])
    # --- reduce (sum / min / max with idx + env): leaves hold the set values; only i < n counts
    for op, pyop, neutral in [("+", sum, 0), ("max", max, 0), ("min", min, INF)]:
        b = pairs_updates(1, "set")
        b.defs.pop("prog"); b.order.remove("prog")
        G.reduce(b, "rd", f"(x (i (n o)))\n  & i ~ $([<] $(n in))\n  & in ~ ?(((* {neutral}) @rdk) (x o))\n", op, idx=True, env=True)
        b.add("@rdk = (* (x x))")
        b.add("""
@prog = ((n ups) out)
  & n ~ {n1 n2}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 L3}}
  & @z ~ (L1 t0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @rd ~ (t (L3 (0 (n2 out))))
""")
        def ref(v, pyop=pyop):
            t = py_updates("set")(v)
            return pyop(t) if pyop is not sum else sum(t) & INF
        ok &= check(f"reduce[{op},idx,env]", b, tup(u24, PAIRS), u24, cases, ref)
    # --- filter_list: indices i < n whose leaf > E
    b = pairs_updates(1, "set"); b.defs.pop("prog"); b.order.remove("prog")
    G.filter_list(b, "fl", "(x (i ((n th) f)))\n  & i ~ $([<] $(n a))\n  & x ~ $([>] $(th c))\n  & a ~ $([&] $(c f))")
    b.add("""
@prog = ((n (th ups)) out)
  & n ~ {n1 n2}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 L3}}
  & @z ~ (L1 t0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @fl ~ (t (L3 (0 ((n2 th) ((0 *) out)))))
""")
    cs = [(n, rng.randrange(1000), u) for n, u in gen_ups(rng)]
    ok &= check("filter_list", b, tup(u24, u24, PAIRS), L_, cs,
                lambda v: [i for i, x in enumerate(py_updates("set")((v[0], v[2]))) if x > v[1]])
    # --- scatter: histogram of leaf values (values < n) over leaves i < n, into an add-trie
    b = pairs_updates(1, "set"); b.defs.pop("prog"); b.order.remove("prog")
    G.update(b, "hadd", "add")
    G.scatter(b, "sc", "hadd", "(x (i (n (x a))))\n  & i ~ $([<] $(n a))")
    b.add("""
@prog = ((n ups) out)
  & n ~ {n1 {n2 n3}}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @z ~ (L1 t0)
  & @z ~ (L4 h0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @sc ~ (t (L3 (0 ((L5 n2) (h0 h)))))
  & @tl ~ (h (L6 (0 (n3 ((0 *) out)))))
""")
    cs = [(n, [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(2 * n + 1))]) for n in [1, 2, 3, 5, 9, 30, 64, 100]]
    def hist(v):
        n, ups = v; t = py_updates("set")(v); h = [0] * n
        for x in t: h[x] += 1
        return h
    ok &= check("scatter(histogram)", b, tup(u24, PAIRS), L_, cs, hist)
    # --- zip2
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.to_list(b, "tl"); G.zip2(b, "zp", "(x (y o))\n  & x ~ $([*] $(y o))")
    b.add("@prog = (n out)\n  & n ~ {n1 n2}\n  & n1 ~ $([-] $(1 m))\n  & @lg ~ (m L)\n  & L ~ {L1 {L2 {L3 L4}}}\n"
          "  & @io ~ (L1 (0 a))\n  & @io ~ (L2 (5 c))\n  & @zp ~ (a (c (L3 t)))\n  & @tl ~ (t (L4 (0 (n2 ((0 *) out)))))")
    ok &= check("zip2", b, u24, L_, [1, 2, 3, 9, 33], lambda n: [i * (5 + i) for i in range(n)])
    # --- multicast: request / deliver; queries answered in query order via a list-with-hole state
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver(b, "dv")
    G.stream(b, "w", 4, "((L (q h)) (k (L3 (q2 h2))))\n  & L ~ {L1 L3}\n  & h ~ (1 (r h2))\n  & @rq ~ (q (k (L1 (r q2))))",
             "((* (q h)) q)\n  & h ~ (0 *)")
    b.add("""
@prog = ((n qs) out)
  & n ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @io ~ (L1 (1000 v))
  & @zq ~ (L2 q0)
  & @w_blk ~ (qs ((L3 (q0 out)) q))
  & @dv ~ (v (q L4))
""")
    cs = [(n, [rng.randrange(n) for _ in range(rng.randrange(3 * n + 1))]) for n in [1, 2, 3, 5, 8, 17, 64, 100] for _ in range(2)]
    ok &= check("mc_request+deliver", b, tup(u24, L_), L_, cs, lambda v: [1000 + k for k in v[1]])
    # --- sssp (frontier + relax + adjacency), directed weighted
    b = G.Book(); G.lg(b); G.sssp(b, "sp"); G.adjacency(b); G.to_list(b, "tl")
    G.stream(b, "w", 8, "((L g) ((u (v w)) (L3 g2)))\n  & L ~ {L1 L3}\n  & @gl_adj ~ (g (u (L1 ((v w) g2))))", "((* g) g)")
    b.add("""
@prog = ((n (s es)) out)
  & n ~ {n0 {n1 n2}}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (s (L3 (16777215 (G D)))))
  & @tl ~ (D (L4 (0 (n2 ((0 *) out)))))
""")
    def dij(v):
        n, s, es = v; d = [INF] * n
        if s >= n: return d
        adj = [[] for _ in range(n)]
        for u, x, w in es: adj[u].append((x, w))
        d[s] = 0; h = [(0, s)]
        while h:
            dd, u = heapq.heappop(h)
            if dd > d[u]: continue
            for x, w in adj[u]:
                if dd + w < d[x]: d[x] = dd + w; heapq.heappush(h, (dd + w, x))
        return d
    cs = [(1, 0, []), (2, 5, [(0, 1, 3)])]
    for n in [2, 3, 5, 9, 20, 64, 100]:
        for _ in range(2):
            cs.append((n, rng.randrange(n), [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 50)) for _ in range(rng.randrange(3 * n))]))
    ok &= check("sssp(frontier+relax)", b, tup(u24, u24, TRIS), L_, cs, dij)
    # --- relax(maximize): max-label propagation (component max id) with enabled/disabled edges (w in {0,1})
    b = G.Book(); G.lg(b); G.relax(b, "mx", maximize=True); G.adjacency(b); G.to_list(b, "tl")
    G.const_trie(b, "z0", "0"); G.iota_trie(b, "io")
    G.stream(b, "w", 8, "((L g) ((u (v w)) (L3 g3)))\n  & L ~ {L1 {L2 L3}}\n  & u ~ {u1 u2}\n  & v ~ {v1 v2}\n  & w ~ {w1 w2}\n"
             "  & @gl_adj ~ (g (u1 (L1 ((v1 w1) g2))))\n  & @gl_adj ~ (g2 (v2 (L2 ((u2 w2) g3))))", "((* g) g)")
    b.add("""
@prog = ((n es) out)
  & n ~ {n0 n2}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @z0 ~ (L3 D0)
  & @io ~ (L4 (0 C0))
  & @mx_loop ~ ((G (D0 (C0 (L5 0)))) D)
  & @tl ~ (D (L6 (0 (n2 ((0 *) out)))))
""")
    def cmax(v):
        n, es = v; p = list(range(n))
        def f(x):
            while p[x] != x: x = p[x]
            return x
        for a, c, w in es:
            if w: p[f(a)] = f(c)
        m = {}
        for i in range(n): m[f(i)] = max(m.get(f(i), 0), i)
        return [m[f(i)] for i in range(n)]
    cs = [(1, [])] + [(n, [(rng.randrange(n), rng.randrange(n), rng.randrange(2)) for _ in range(rng.randrange(2 * n))])
                      for n in [2, 3, 5, 9, 20, 64, 100] for _ in range(2)]
    ok &= check("relax(maximize)", b, tup(u24, TRIS), L_, cs, cmax)
    # ================= v2 primitives (added while composing the exp8 programs)
    # --- dec act
    ok &= check("update[dec]+stream", pairs_updates(1, "dec"), tup(u24, PAIRS), L_, cases,
                lambda v: [(-sum(1 for k, _ in v[1] if k == i)) & INF for i in range(v[0])])
    # --- mc_deliver_keep: answers in query order AND the kept copy of the value trie
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver_keep(b, "dk")
    G.to_list(b, "tl")
    G.stream(b, "w", 4, "((L (q h)) (k (L3 (q2 h2))))\n  & L ~ {L1 L3}\n  & h ~ (1 (r h2))\n  & @rq ~ (q (k (L1 (r q2))))",
             "((* (q h)) q)\n  & h ~ (0 *)")
    b.add("""
@prog = ((n qs) (ans cp))
  & n ~ {n0 n1}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & @io ~ (L1 (1000 v))
  & @zq ~ (L2 q0)
  & @w_blk ~ (qs ((L3 (q0 ans)) q))
  & @dk ~ (v (q (L4 v2)))
  & @tl ~ (v2 (L5 (0 (n1 ((0 *) cp)))))
""")
    cs = [(n, [rng.randrange(n) for _ in range(rng.randrange(3 * n + 1))]) for n in [1, 2, 3, 5, 8, 17, 64, 100]]
    ok &= check("mc_deliver_keep", b, tup(u24, L_), tup(L_, L_), cs, lambda v: ([1000 + k for k in v[1]], [1000 + i for i in range(v[0])]))
    # --- zip2e
    b = G.Book(); G.lg(b); G.iota_trie(b, "io"); G.to_list(b, "tl")
    G.zip2e(b, "ze", "(x (y (e o)))\n  & x ~ $([*] $(y p))\n  & p ~ $([+] $(e o))")
    b.add("@prog = ((n e) out)\n  & n ~ {n1 n2}\n  & n1 ~ $([-] $(1 m))\n  & @lg ~ (m L)\n  & L ~ {L1 {L2 {L3 L4}}}\n"
          "  & @io ~ (L1 (0 a))\n  & @io ~ (L2 (5 c))\n  & @ze ~ (a (c (L3 (e t))))\n  & @tl ~ (t (L4 (0 (n2 ((0 *) out)))))")
    ok &= check("zip2e", b, tup(u24, u24), L_, [(1, 3), (2, 0), (9, 7), (33, 1)], lambda v: [i * (5 + i) + v[1] for i in range(v[0])])
    # --- bcast: every outer copy gets the same inner keyed add; read back the combined trie (depth Lo + Li)
    b = G.Book(); G.const_trie(b, "z0", "0"); G.update(b, "ad", "add"); G.bcast(b, "bc", "ad"); G.to_list(b, "tl")
    G.stream(b, "w", 4, "((A (B t)) ((k p) (A2 (B2 t2))))\n  & A ~ {A1 A2}\n  & B ~ {B1 B2}\n  & @bc ~ (t (A1 ((B1 (k p)) t2)))",
             "((* (* t)) t)")
    b.add("""
@prog = ((lo (li ups)) out)
  & lo ~ {lo1 {lo2 lo3}}
  & li ~ {li1 {li2 li3}}
  & lo1 ~ $([+] $(li1 lc))
  & lc ~ {lc1 {lc2 lc3}}
  & @z0 ~ (lc1 t0)
  & @w_blk ~ (ups ((lo2 (li2 t0)) t))
  & 1 ~ $([<<] $(lc2 cnt))
  & @tl ~ (t (lc3 (0 (cnt ((0 *) out)))))
  & lo3 ~ *
  & li3 ~ *
""")
    def bc(v):
        lo, li, ups = v; inner = [0] * (1 << li)
        for k, p in ups: inner[k] += p
        return inner * (1 << lo)
    cs = [(lo, li, [(rng.randrange(1 << li), rng.randrange(100)) for _ in range(rng.randrange(12))]) for lo in [0, 1, 2, 3] for li in [0, 1, 3]]
    ok &= check("bcast", b, tup(u24, u24, PAIRS), L_, cs, bc)
    # --- mapreduce: min over leaves (i < n) and the rebuilt trie with every leaf + 1
    b = pairs_updates(1, "set"); b.defs.pop("prog"); b.order.remove("prog")
    G.mapreduce(b, "mr", "(x (i (n (x2 r))))\n  & x ~ {xa xb}\n  & xa ~ $([+1] x2)\n  & i ~ $([<] $(n in))\n"
                "  & in ~ ?(((* 16777215) @gl_sel2) (xb r))", "min")
    b.add("""
@prog = ((n ups) (mn lst))
  & n ~ {n1 {n2 n3}}
  & n1 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @z ~ (L1 t0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @mr ~ (t (L3 (0 (n2 (t2 mn)))))
  & @tl ~ (t2 (L4 (0 (n3 ((0 *) lst)))))
""")
    ok &= check("mapreduce[min]", b, tup(u24, PAIRS), tup(u24, L_), cases,
                lambda v: (min(py_updates("set")(v)), [x + 1 for x in py_updates("set")(v)]))
    # --- iterate: sum of 0..n-1 by a sequential loop (state (k (n acc)))
    b = G.Book(); G.iterate(b, "it", """((k (n acc)) ((k4 (n2 acc2)) go))
  & k ~ {k1 k2}
  & acc ~ $([+] $(k1 acc2))
  & k2 ~ $([+1] kk)
  & kk ~ {k3 k4}
  & n ~ {n1 n2}
  & k3 ~ $([<] $(n1 go))""")
    b.add("@prog = (n out)\n  & @it_it ~ ((0 (n 0)) (* (* out)))")
    ok &= check("iterate", b, u24, u24, [1, 2, 3, 10, 50], lambda n: sum(range(n)))
    # --- peek act: copy the list at key k out of an adjacency trie, keep the trie
    b = G.Book(); G.lg(b); G.adjacency(b); G.update(b, "pk", "peek"); G.to_list(b, "tl")
    G.stream(b, "w", 4, "((L g) ((u v) (L3 g2)))\n  & L ~ {L1 L3}\n  & @gl_adj ~ (g (u (L1 ((v 0) g2))))", "((* g) g)")
    b.add("""
@prog = ((n (k es)) (cp all))
  & n ~ {n0 n1}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @pk ~ (G (k (L3 (cp G2))))
  & @tl ~ (G2 (L4 (0 (n1 ((0 *) all)))))
""")
    def pk(v):
        n, k, es = v; a = [[] for _ in range(n)]
        for u, x in es: a[u] = [(x, 0)] + a[u]
        return (a[k], a)
    cs = [(n, rng.randrange(n), [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(2 * n + 1))]) for n in [1, 2, 5, 9, 40]]
    ok &= check("update[peek]", b, tup(u24, u24, PAIRS), tup(list_of(tup(u24, u24)), list_of(list_of(tup(u24, u24)))), cs, pk)
    # --- POP24 leaf helper inside a reduce
    b = pairs_updates(1, "set"); b.defs.pop("prog"); b.order.remove("prog")
    G.reduce(b, "pc", "(x o)\n" + G.POP24, "+")
    b.add("""
@prog = ((n ups) out)
  & n ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 L3}}
  & @z ~ (L1 t0)
  & @w_blk ~ (ups ((L2 t0) t))
  & @pc ~ (t (L3 out))
""")
    cs = [(n, [(rng.randrange(n), rng.randrange(1 << 24)) for _ in range(rng.randrange(2 * n + 1))]) for n in [1, 2, 5, 9, 40, 64]]
    ok &= check("POP24 (in reduce)", b, tup(u24, PAIRS), u24, cs, lambda v: sum(bin(x).count("1") for x in py_updates("set")(v)))
    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
