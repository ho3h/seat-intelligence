"""Scope analysis: how much of the graphprims primitives (24) and recipes (15) is data-oblivious enough to normalize, and what stops it.
Each entry definition is called with OPEN wires (one free wire per port of its declared signature) and reduced with the strict engine.
Two regimes: (open) every port free; (shape) the trie-depth ports are set to the literal 3, everything else free.
usage: python3 -m genome.hero2.scope OUT.json"""
import json, sys
from collections import Counter
from genome import netast
from genome.lib.glue import Program, NUM, DEPTH, TRIE, ADJ, EDGE, LIST, WEDGE, Port, TUP
from genome.lib import recipes as R
from genome.hero2 import inet as I


def sig_tree(sig, plug=None):
    plug = plug or {}
    if isinstance(sig, Port):
        if sig.dir == "in" and sig.name in plug: return str(plug[sig.name])
        if sig.fields:
            names = [(n if sig.dir == "in" else "o_" + n) for n, _ in sig.fields]
            t = names[-1]
            for n in reversed(names[:-1]): t = f"({n} {t})"
            return t
        return sig.name
    if isinstance(sig, tuple): return f"({sig_tree(sig[0], plug)} {sig_tree(sig[1], plug)})"
    return str(sig)


def depth_ports(sig):
    out = []
    if isinstance(sig, Port):
        if sig.dir == "in" and getattr(sig.kind, "tag", None) == "depth": out.append(sig.name)
    elif isinstance(sig, tuple):
        out += depth_ports(sig[0]) + depth_ports(sig[1])
    return out


def deps_of(net, i):
    """open ports (F names) that the stuck node i waits on, following data flow backwards from its principal port:
    through the result port of an operator (to its operands), through a copy of a duplicator or constructor (to its principal)."""
    out, seen = set(), set()

    def back(port):
        if port < 0: return
        m, s = port // 3, port % 3
        if (m, s) in seen or net.kind[m] is None: return
        seen.add((m, s))
        k = net.kind[m]
        if k == "F": out.add(net.val[m]); return
        if k == "O" and s == 2: back(net.p[m][0]); back(net.p[m][1]); return
        if k in ("D", "C") and s in (1, 2): back(net.p[m][0]); return
    back(net.p[i][0])
    return out


def analyse(book_text, entry, tree_text, fuel=300000):
    import re
    vs = re.findall(r"[A-Za-z_]\w*", tree_text)
    assert len(vs) == len(set(vs)), f"duplicate wire names in the open call: {tree_text}"
    reg = I.Registry().add_book(book_text, "").finalize()
    ast = netast.parse_book("@t = " + tree_text)[0]["t"][0]
    net = I.build_trees(None, [(False, ("ref", entry), ast)])
    eng = I.Engine(reg)
    ok = eng.run(net, fuel)
    cnt = I.ncount(net)
    stuck_S = [i for i, k in enumerate(net.kind) if k == "S"]
    stuck_O = [i for i, k in enumerate(net.kind) if k == "O"]
    data_S = [i for i in stuck_S if deps_of(net, i)]
    blockers = Counter()
    for i in data_S:
        for n in deps_of(net, i): blockers[n] += 1
    refs = [net.val[i] for i, k in enumerate(net.kind) if k == "R"]
    rec_refs = sorted({r for r in refs if r in reg.defs and reg.defs[r].rec})
    if not ok: cls = "E diverges (fuel)"
    elif data_S: cls = "C branches on open data"
    elif refs: cls = "D blocked on unexpanded (recursive/branch) definitions"
    elif stuck_S: cls = "D blocked on unexpanded (recursive/branch) definitions"
    elif stuck_O: cls = "B branch-free symbolic arithmetic"
    else: cls = "A pure plumbing"
    return {"terminates": ok, "interactions": net.itrs, "residual_nodes": dict(cnt), "switches_on_open_data": len(data_S),
            "switches_total": len(stuck_S), "operators_stuck": len(stuck_O), "blocked_by_open_ports": dict(blockers),
            "unexpanded_refs": len(refs), "recursive_refs_left": rec_refs, "class": cls, "flags": sorted(net.flags)}


def spine_plug(sig, n=3):
    """plug: depth ports -> n ; list ports of numbers -> a concrete spine of n cells with open elements"""
    plug = {}
    def walk(x):
        if isinstance(x, Port):
            if x.dir == "in":
                tag = getattr(x.kind, "tag", None)
                if tag == "depth": plug[x.name] = n
                elif tag == "list":
                    cells = "(0 *)"
                    for j in reversed(range(n)): cells = f"(1 ({x.name}{j} {cells}))"
                    plug[x.name] = cells
        elif isinstance(x, tuple): walk(x[0]); walk(x[1])
    walk(sig)
    return plug


def build_prims():
    P = Program()
    prims = {}
    prims["lg"] = P.lg()
    prims["const_trie"] = P.const_trie("ct", 0)
    prims["iota_trie"] = P.iota_trie("io")
    prims["update"] = P.update("up", "inc")
    prims["get"] = P.get("gt")
    prims["reduce"] = P.reduce("rd", lambda d, x: x, "+")
    prims["fold"] = P.fold("fd", lambda d, x, i, acc: (d.erase(i), d.op(acc, "+", x))[1], NUM)
    prims["to_list"] = P.to_list("tl")
    prims["filter_list"] = P.filter_list("fl", lambda d, x, i, E: (d.erase(i), d.op(x, ">", E))[1])
    upd = P.update("scup", "add")
    prims["scatter"] = P.scatter("sc", upd, lambda d, x, i, E: (d.erase(E), (x, i))[1])
    prims["zip2"] = P.zip2("z2", lambda d, x, y: d.op(x, "+", y))
    prims["zip2e"] = P.zip2e("z2e", lambda d, x, y, E: (d.erase(E), d.op(x, "+", y))[1], NUM)
    prims["bcast"] = P.bcast("bc", P.update("bcu", "inc"))
    prims["mapreduce"] = P.mapreduce("mr", lambda d, x, i: (x, i), "+")
    def body(d, n, c):
        n1, n2 = d.fanout(n, 2)
        return d.op(n1, "+", 1), c, d.op(n2, "<", 10)
    prims["iterate"] = P.iterate("it", body, [("n", NUM), ("c", NUM)])
    prims["mc_empty"] = P.mc_empty("mce")
    prims["mc_request"] = P.mc_request("mcr")
    prims["mc_deliver"] = P.mc_deliver("mcd")
    prims["mc_deliver_keep"] = P.mc_deliver_keep("mck")
    inc = P.update("dinc", "inc")
    def step(d, L, h, u, v):
        L1, L2, L3 = d.fanout(L, 3)
        return L3, d.call(inc, t=d.call(inc, t=h, k=u, L=L1), k=v, L=L2)
    def fin(d, L, h): d.erase(L); return h
    prims["stream"] = P.stream("w", step, fin, state=[("L", DEPTH), ("h", TRIE(NUM))], elem=EDGE)
    def fact(d, X, dv, c):
        d.erase(X)
        c1, c2 = d.fanout(c, 2)
        return d.op(dv, "+", c1), d.op(c2, ">", 0), 0
    def fmsg(d, m, w):
        d.erase(w)
        return m
    prims["frontier"] = P.frontier("fr", fact, fmsg, "add", 0)
    prims["relax"] = P.relax("rl")
    prims["sssp"] = P.sssp("ss")
    prims["adjacency"] = P.adjacency()
    return P, prims


def build_recipes():
    P = Program()
    r = {}
    r["list_length_and_copy"] = R.list_length_and_copy(P, "lc", NUM, copies=2)
    r["list_to_trie"] = R.list_to_trie(P, "lt", NUM)
    r["filter_in_order"] = R.filter_in_order(P, "fio", NUM, lambda d, x, E: R.ge(d, x, E), env=NUM)
    r["count_where"] = R.count_where(P, "cw", NUM, lambda d, x: x)
    r["take_first"] = R.take_first(P, "tf", NUM)
    r["argmax_first"] = R.argmax_first(P, "am", NUM, lambda d, x: x)
    r["sort_by"] = R.sort_by(P, "sb", NUM, lambda d, x: x)
    r["lookup_many"] = R.lookup_many(P, "lm", NUM, lambda d, k: k)
    r["reduce_by_key"] = R.reduce_by_key(P, "rbk", NUM, lambda d, k: k, combine="inc")
    r["select_sorted"] = R.select_sorted(P, "ssel", lambda d, x, i, E: (d.erase(E, i), d.op(x, ">", 0))[1] if False else (d.erase(i, E), x)[1],
                                         lambda d, x, i, E: (d.erase(E, x), i)[1])
    r["count_where_trie"] = R.count_where_trie(P, "cwt", lambda d, x, i, E: (d.erase(i, E), x)[1])
    r["argmax_first_trie"] = R.argmax_first_trie(P, "amt", lambda d, x, i, E: (d.erase(i, E), (1, x))[1])
    r["frontier_relax"] = R.frontier_relax(P, "frx")
    r["layered_bfs_count"] = R.layered_bfs_count(P, "lbc")
    r["pointer_jump"] = R.pointer_jump(P, "pj")
    return P, r


def main():
    out = {"primitives": {}, "recipes": {}}
    for kind, (P, items) in (("primitives", build_prims()), ("recipes", build_recipes())):
        text = P.book.text()
        for name, prim in items.items():
            rec = {"entry": prim.entry}
            try:
                open_ = analyse(text, prim.entry, sig_tree(prim.sig))
                dps = depth_ports(prim.sig)
                shape = analyse(text, prim.entry, sig_tree(prim.sig, {p: 3 for p in dps}))
                spine = analyse(text, prim.entry, sig_tree(prim.sig, spine_plug(prim.sig, 3)))
                rec.update(open=open_, shape=shape, spine=spine, depth_ports=dps)
            except Exception as e:
                import traceback; traceback.print_exc()
                rec["error"] = repr(e)[:200]
            out[kind][name] = rec
            print(f"{kind[:4]} {name:22s} open: {rec['open']['class'][:26]:26s} | depth=3: {rec['shape']['class'][:26]:26s} | +list spine 3: {rec['spine']['class'][:26]:26s} (itrs {rec['open']['interactions']}/{rec['shape']['interactions']}/{rec['spine']['interactions']})", flush=True)
    json.dump(out, open(sys.argv[1], "w"), indent=1)


main()
