"""Swing 20, must-not-link step: the ordered greedy (RECONCILIATION-SPEC step 4, no size cap) as HVM2 nets, one independent
net per conflicted component (the partition route: "split the workload into partitions processed by independent nets and
merged").

Pipeline: main net (genome/exp16/net.py) -> canon + conflicts (checked exactly) -> host groups the conflicted components
(group-by on the verified canon) -> one greedy net per conflicted component -> host overwrites those members' canon ->
compare with the full greedy over the whole slice (Python reference).

Greedy net, input (H, T, E, M):
  T  perfect tree of height H of cells (x c): member x with component label c (= x at start); padding (16777215 0)
  E  list of accepted edges (u v) of the component, in processing order (descending score, ties ascending (u, v))
  M  list of must-not-link pairs (a b) inside the component, rewritten in component labels as merges happen
Output (C, K): C list of (x c) final labels (label = largest member), K list of skipped merges (u v).
Per edge, with no switch on the state's critical path:
  cu, cv   = sum over cells of (x==u)*c, (x==v)*c          (tree reduce, depth ~2H)
  blocked  = OR over M of {a, b} == {cu, cv}                  (list walk, M is tiny)
  g        = (cu != cv) & !blocked ; nc = max(cu, cv)
  c'       = c + g*((c==cu)|(c==cv))*(nc - c) at every cell and in M   (tree map, broadcast ~1 rewrite per level)
The next edge's lookups start at each leaf as soon as that leaf is relabelled (pipelined).
usage: python3 -m genome.exp16.greedy N...
"""
from __future__ import annotations
import json, os, sys, collections
from .data import slice_
from .run import reference, greedy_mnl, _timed, _parse, HVM, HVM_DEPTH, ROOT, RUNS
from ..types import tup, u24, list_of, decode

PAD = 16777215
NET = r"""
@prog = ((H (T (E M))) (C K))
  & @fold ~ (E (H (T (M (K (Tf Hf))))))
  & @of ~ (Tf (Hf ((0 *) C)))

@fold = ((?((@f_nil @f_cons) (pl (H (T (M (os out)))))) pl) (H (T (M (os out)))))
@f_nil = (* (H (T (* ((0 *) (T H))))))
@f_cons = (* (((u v) rest) (H (T (M (os out))))))
  & H ~ {H1 {H2 H3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @fd ~ (T (H1 (u1 (v1 (T1 (cu cv))))))
  & cu ~ {cu1 {cu2 {cu3 {cu4 {cu5 cu6}}}}}
  & cv ~ {cv1 {cv2 {cv3 {cv4 cv5}}}}
  & @blk ~ (M (cu1 (cv1 (M1 bl))))
  & cu2 ~ $([!] $(cv2 ne))
  & bl ~ {bl1 bl2}
  & ne ~ {ne1 ne2}
  & bl1 ~ $([^] $(1 nb))
  & ne1 ~ $([&] $(nb g))
  & ne2 ~ $([&] $(bl2 sk))
  & cu3 ~ $([<] $(cv3 lt))
  & cv4 ~ $([-] $(cu4 dd))
  & lt ~ $([*] $(dd ad))
  & cu5 ~ $([+] $(ad nc))
  & {Pa Pb} ~ (cu6 (cv5 (nc g)))
  & @rl ~ (T1 (H2 (Pa T2)))
  & @rlm ~ (M1 (Pb M2))
  & sk ~ ?((@ns @ys) (u2 (v2 (os os2))))
  & @fold ~ (rest (H3 (T2 (M2 (os2 out)))))
@ns = (* (* (o o)))
@ys = (* (u (v ((1 ((u v) o)) o))))

// fd: (cu, cv) = labels of u and v; the tree is rebuilt unchanged
@fd = (t (H (u (v (t2 (cu cv))))))
  & H ~ ?((@fd_leaf @fd_node) (t (u (v (t2 (cu cv))))))
@fd_leaf = ((x c) (u (v ((x3 c3) (cu cv)))))
  & x ~ {x1 {x2 x3}}
  & c ~ {c1 {c2 c3}}
  & x1 ~ $([=] $(u eu))
  & x2 ~ $([=] $(v ev))
  & eu ~ $([*] $(c1 cu))
  & ev ~ $([*] $(c2 cv))
@fd_node = (hm ((l r) (u (v ((l2 r2) (cu cv))))))
  & hm ~ {h1 h2}
  & u ~ {ua ub}
  & v ~ {va vb}
  & @fd ~ (l (h1 (ua (va (l2 (cul cvl))))))
  & @fd ~ (r (h2 (ub (vb (r2 (cur cvr))))))
  & cul ~ $([+] $(cur cu))
  & cvl ~ $([+] $(cvr cv))

// blk: 1 iff some pair (a b) of M has {a, b} == {cu, cv}; M rebuilt
@blk = ((?((@bk_nil @bk_cons) (pl (cu (cv (m1 bl))))) pl) (cu (cv (m1 bl))))
@bk_nil = (* (* (* ((0 *) 0))))
@bk_cons = (* (((a b) rest) (cu (cv ((1 ((a3 b3) rest2)) bl)))))
  & a ~ {a1 {a2 a3}}
  & b ~ {b1 {b2 b3}}
  & cu ~ {cu1 {cu2 cu3}}
  & cv ~ {cv1 {cv2 cv3}}
  & a1 ~ $([=] $(cu1 e1))
  & b1 ~ $([=] $(cv1 e2))
  & a2 ~ $([=] $(cv2 e3))
  & b2 ~ $([=] $(cu2 e4))
  & e1 ~ $([&] $(e2 h1))
  & e3 ~ $([&] $(e4 h2))
  & h1 ~ $([|] $(h2 h))
  & h ~ $([|] $(blr bl))
  & @blk ~ (rest (cu3 (cv3 (rest2 blr))))

// rlc: relabel one label c with the bundle (cu cv nc g)
@rlc = (c ((cu (cv (nc g))) c2))
  & c ~ {c1 {cx {c3 c4}}}
  & c1 ~ $([=] $(cu m1))
  & cx ~ $([=] $(cv m2))
  & m1 ~ $([|] $(m2 m))
  & m ~ $([&] $(g gm))
  & nc ~ $([-] $(c3 d))
  & gm ~ $([*] $(d e))
  & c4 ~ $([+] $(e c2))
@rl = (t (H (P t2)))
  & H ~ ?((@rl_leaf @rl_node) (t (P t2)))
@rl_node = (hm ((l r) (P (l2 r2))))
  & hm ~ {h1 h2}
  & P ~ {Pa Pb}
  & @rl ~ (l (h1 (Pa l2)))
  & @rl ~ (r (h2 (Pb r2)))
@rl_leaf = ((x c) (P (x c2)))
  & @rlc ~ (c (P c2))
@rlm = ((?((@rm_nil @rm_cons) (pl (P o))) pl) (P o))
@rm_nil = (* (* (0 *)))
@rm_cons = (* (((a b) rest) (P (1 ((a2 b2) rest2)))))
  & P ~ {Pa {Pb Pc}}
  & @rlc ~ (a (Pa a2))
  & @rlc ~ (b (Pb b2))
  & @rlm ~ (rest (Pc rest2))

// of: the real cells (x c) in tree order
@of = (t (H (tail o)))
  & H ~ ?((@of_leaf @of_node) (t (tail o)))
@of_node = (hm ((l r) (tail o)))
  & hm ~ {h1 h2}
  & @of ~ (l (h1 (mid o)))
  & @of ~ (r (h2 (tail mid)))
@of_leaf = ((x c) (tail o))
  & x ~ {x1 x2}
  & x1 ~ $([!] $(16777215 keep))
  & keep ~ ?(((* (t t)) (* (e (t2 (1 (e t2)))))) ((x2 c) (tail o)))
"""
OUT_T = tup(list_of(tup(u24, u24)), list_of(tup(u24, u24)))


def component_inputs(s, canon, conflicts):
    """Group-by on the (verified) canon: per conflicted component, its members, ordered accepted edges and MNL pairs."""
    tau = s["tau"]; bad = sorted({c for a, b, c in conflicts})
    mem, E, M = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
    for i, c in enumerate(canon):
        if c in bad: mem[c].append(i)
    for u, v, sc in sorted((e for e in s["edges"] if e[2] >= tau), key=lambda e: (-e[2], e[0], e[1])):
        if canon[u] in bad: E[canon[u]].append((u, v))
    for a, b in s["mnl"]:
        if canon[a] in bad and canon[a] == canon[b]: M[canon[a]].append((a, b))
    return [(c, mem[c], E[c], M[c]) for c in bad]


def nest(items, tail="(0 *)"):
    out = tail
    for x in reversed(items): out = f"(1 ({x} {out}))"
    return out


def encode(mem, E, M):
    H = 0
    while (1 << H) < len(mem): H += 1
    cells = [f"({x} {x})" for x in mem] + [f"({PAD} 0)"] * ((1 << H) - len(mem))
    while len(cells) > 1: cells = [f"({cells[i]} {cells[i + 1]})" for i in range(0, len(cells), 2)]
    return f"({H} ({cells[0]} ({nest([f'({u} {v})' for u, v in E])} {nest([f'({a} {b})' for a, b in M])})))", H


def run_component(mem, E, M, mode="run"):
    root, H = encode(mem, E, M)
    text = f"@main = r\n  & @prog ~ ({root} r)\n" + NET
    path = os.path.join(ROOT, "scratch", f"exp16_greedy_{os.getpid()}.hvm"); open(path, "w").write(text)
    try:
        out, err, wall, rss = _timed([HVM_DEPTH if mode == "depth" else HVM, "run", path], 600)
    finally:
        os.unlink(path)
    return _parse(out), H


if __name__ == "__main__":
    for N in map(int, sys.argv[1:]):
        s = slice_(N); canon, conf = reference(s)
        full, full_sk = greedy_mnl(s)
        final = list(canon); skipped = []; depths = []; itrs = 0; ok = True
        for c, mem, E, M in component_inputs(s, canon, conf):
            r, H = run_component(mem, E, M)
            got = decode(r["result"], OUT_T)
            for x, lab in got[0]: final[x] = lab
            skipped += got[1]; itrs += r["itrs"]
            d, _ = run_component(mem, E, M, "depth")
            depths.append(dict(members=len(mem), edges=len(E), mnl=len(M), depth=d["depth"], itrs=d["itrs"]))
        rec = dict(N=N, components=len(depths), equals_full_greedy=(final == full and sorted(map(tuple, skipped)) == sorted(full_sk)),
                   skipped=len(skipped), greedy_itrs=itrs, max_depth=max(x["depth"] for x in depths),
                   sum_depth=sum(x["depth"] for x in depths), per_component=depths)
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "greedy_net.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
