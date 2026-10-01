"""Swing 20 net: reconciliation core on tree-shaped input (hand-written HVM2 text; nothing learned or searched).

Input  (n, L, tau, E, HE, M, HM):
  E  perfect binary tree of height HE (internal node `(l r)`, leaf `(u (v s))`), padded with rejected dummies (0,1,0).
  M  perfect binary tree of height HM of must-not-link pairs, leaf `(a (b live))`, padded with live = 0.
Output (canon, conflicts):
  canon      list, entry i = largest member id of i's component under the accepted edges (s >= tau)
  conflicts  list of (a, b, c) for every live must-not-link pair whose ends ended up in one component c, in M order.

How it reads the input shallowly (the change vs runs/exp10, whose linked-list read was Theta(m) deep):
  1. Every accepted edge leaf makes two fresh wires c1, c2 and a SPARSE vertex trie with two paths (to u and to v) whose
     leaf payloads are one-element DIFFERENCE LISTS holding the channel ends (c2 c1) and (c1 c2). Rejected leaves give
     the empty trie. Every must-not-link leaf does the same with two probe wires (in the probe half of the payload).
  2. Sparse tries are merged pairwise up the edge tree (@mg): empty sides are taken as is, two present nodes recurse, and
     two leaf payloads concatenate their difference lists by pure wiring (no traversal). Depth ~ c*(HE + L), pipelined.
  3. @dz densifies the merged trie (absent subtrees -> generated leaves (i, [])) and closes the difference lists.
  4. Label propagation over the pre-wired channels, pipelined termination: runs/exp10 cc_pipe, unchanged.
  5. @pz sends each vertex's final label into its probe wires; each must-not-link leaf compares the two labels it gets.
  6. canon list: runs/exp10 tl_leafmap (tail threaded, all cells in parallel).
"""
from __future__ import annotations
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "runs", "exp10"))
from lib_ext import cc_pipe, tl_leafmap, lib  # noqa: E402

CORE = r"""
@prog = ((n (L (tau (E (HE (M HM)))))) (C F))
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 L7}}}}}}
  & @ew ~ (HE ((L1 tau) (E te)))
  & @mw ~ (HM (L2 (M (tm ((0 *) F)))))
  & @mg ~ (L3 (te (tm T)))
  & @dz ~ (T (L4 (0 (S P))))
  & @A_loop ~ (L5 (S Sf))
  & @pz ~ (Sf (P (L6 S2)))
  & @A_tl ~ (S2 (L7 (0 (n ((0 *) C)))))

// ---- sparse trie path: key k, remaining depth L, leaf payload P. Node = (1 (l r)), empty = (0 *), leaf = (1 P)
@pa = (k (L (P o)))
  & L ~ ?((@pa_leaf @pa_node) (k (P o)))
@pa_leaf = (* (P (1 P)))
@pa_node = (lm (k (P (1 kids))))
  & k ~ {k1 k2}
  & lm ~ {l1 l2}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 b))
  & b ~ ?((@pa_L @pa_R) (k2 (l2 (P kids))))
@pa_L = (k (L (P (sub (0 *)))))
  & @pa ~ (k (L (P sub)))
@pa_R = (* (k (L (P ((0 *) sub)))))
  & @pa ~ (k (L (P sub)))

// ---- merge two sparse tries of remaining depth L; leaf payloads (C P) are pairs of difference lists (hole result)
@mg = (L (a (b o)))
  & a ~ (ta pa)
  & ta ~ ?((@mg_a0 @mg_a1) (pa (L (b o))))
@mg_a0 = (* (* (b b)))
@mg_a1 = (* (pa (L (b o))))
  & b ~ (tb pb)
  & tb ~ ?((@mg_b0 @mg_b1) (pa (pb (L o))))
@mg_b0 = (pa (* (* (1 pa))))
@mg_b1 = (* (pa (pb (L (1 po)))))
  & L ~ ?((@mg_lf @mg_nd) (pa (pb po)))
@mg_lf = (((x ar) (y qr)) (((bh x) (qh y)) ((bh ar) (qh qr))))
@mg_nd = (lm ((al ar) ((bl br) (ol or))))
  & lm ~ {l1 l2}
  & @mg ~ (l1 (al (bl ol)))
  & @mg ~ (l2 (ar (br or)))

// ---- edge tree walk: height h, K = (L tau) -> sparse trie of channel ends
@ew = (h (K (e t)))
  & h ~ ?((@ew_leaf @ew_node) (K (e t)))
@ew_node = (hm ((L tau) ((el er) t)))
  & hm ~ {h1 h2}
  & L ~ {L1 {L2 L3}}
  & tau ~ {t1 t2}
  & @ew ~ (h1 ((L1 t1) (el tl)))
  & @ew ~ (h2 ((L2 t2) (er tr)))
  & @mg ~ (L3 (tl (tr t)))
@ew_leaf = ((L tau) ((u (v s)) t))
  & s ~ $([<] $(tau rej))
  & rej ~ ?((@ew_acc @ew_rej) (L (u (v t))))
@ew_rej = (* (* (* (* (0 *)))))
@ew_acc = (L (u (v t)))
  & L ~ {L1 {L2 L3}}
  & @pa ~ (u (L1 (((h1 (1 ((c2 c1) h1))) (q1 q1)) pu)))
  & @pa ~ (v (L2 (((h2 (1 ((c1 c2) h2))) (q2 q2)) pv)))
  & @mg ~ (L3 (pu (pv t)))

// ---- must-not-link tree walk -> sparse trie of probe wires + difference list of conflicts (a b c)
@mw = (h (L (m (t r))))
  & h ~ ?((@mw_leaf @mw_node) (L (m (t r))))
@mw_node = (hm (L ((ml mr) (t (rh rr)))))
  & hm ~ {h1 h2}
  & L ~ {L1 {L2 L3}}
  & @mw ~ (h1 (L1 (ml (tl (x rr)))))
  & @mw ~ (h2 (L2 (mr (tr (rh x)))))
  & @mg ~ (L3 (tl (tr t)))
@mw_leaf = (L ((a (b live)) (t r)))
  & live ~ ?((@mw_dead @mw_live) (L (a (b (t r)))))
@mw_dead = (* (* (* ((0 *) (q q)))))
@mw_live = (* (L (a (b (t (rh rr))))))
  & L ~ {L1 {L2 L3}}
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & @pa ~ (a1 (L1 (((h1 h1) (g1 (1 (wa g1)))) pu)))
  & @pa ~ (b1 (L2 (((h2 h2) (g2 (1 (wb g2)))) pv)))
  & @mg ~ (L3 (pu (pv t)))
  & wa ~ {la1 la2}
  & la1 ~ $([=] $(wb eq))
  & eq ~ ?((@mw_ne @mw_eq) (a2 (b2 (la2 (rh rr)))))
@mw_ne = (* (* (* (h h))))
@mw_eq = (* (a (b (l (h (1 ((a (b l)) h)))))))

// ---- densify: sparse trie -> dense trie S of (i ch) leaves and dense trie P of probe lists
@dz = (t (L (base (S P))))
  & t ~ (tg pl)
  & tg ~ ?((@dz_e @dz_p) (pl (L (base (S P)))))
@dz_e = (* (L (base (S P))))
  & L ~ {L1 L2}
  & @mk ~ (L1 (base (1 S)))
  & @zl ~ (L2 P)
@dz_p = (* (pl (L (base (S P)))))
  & L ~ ?((@dz_leaf @dz_node) (pl (base (S P))))
@dz_leaf = ((((0 *) ch) ((0 *) pr)) (b ((b ch) pr)))
@dz_node = (lm ((a c) (base ((Sa Sc) (Pa Pc)))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @dz ~ (a (l1 (b1 (Sa Pa))))
  & @dz ~ (c (l2 (bR (Sc Pc))))

// ---- after LP: send every final label into the vertex's probe wires; leaves become (x 0)
@pz = (s (p (L o)))
  & L ~ ?((@pz_leaf @pz_node) (s (p o)))
@pz_leaf = ((x *) (pr (y 0)))
  & @sd ~ (pr (x y))
@pz_node = (lm ((sa sc) ((pa pc) (oa oc))))
  & lm ~ {l1 l2}
  & @pz ~ (sa (pa (l1 oa)))
  & @pz ~ (sc (pc (l2 oc)))
@sd = ((?((@sd_nil @sd_cons) (pl (x y))) pl) (x y))
@sd_nil = (* (x x))
@sd_cons = (* ((p rest) (x y)))
  & x ~ {p x2}
  & @sd ~ (rest (x2 y))
"""


FAN = r"""
// ---- fan: joins two channel-likes (i o) into one, as a persistent process. The value from above is copied into both
// children at once (DUP chain, ~1 rewrite per level); only the recursion waits on a switch (gate: one round per value)
@fan = (A (B (I O)))
  & @fl ~ (O (I (A B)))
@fl = ((x O2) (I ((ia oa) (ib ob))))
  & x ~ {x1 {x2 x3}}
  & oa ~ (x1 oa2)
  & ob ~ (x2 ob2)
  & x3 ~ ?((@fl_go (* @fl_go)) (O2 (I ((ia oa2) (ib ob2)))))
@fl_go = (O2 (I ((ia oa2) (ib ob2))))
  & ia ~ (ya ia2)
  & ib ~ (yb ib2)
  & ya ~ {a1 a2}
  & yb ~ {b1 b2}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?(((a (* a)) (* (* (b b)))) (a2 (b2 y)))
  & I ~ (y I2)
  & @fl ~ (O2 (I2 ((ia2 oa2) (ib2 ob2))))
"""


def fan_variant(core):
    """Channels per vertex as a tree of persistent fan processes instead of a list walked each round: a vertex of degree d
    pays O(depth of its join tree) per LP round instead of O(d)."""
    rep = [
        ("(((h1 (1 ((c2 c1) h1))) (q1 q1)) pu)", "(((c2 c1) (q1 q1)) pu)"),
        ("(((h2 (1 ((c1 c2) h2))) (q2 q2)) pv)", "(((c1 c2) (q2 q2)) pv)"),
        ("(((h1 h1) (g1 (1 (wa g1)))) pu)", "(((@A_zs *) (g1 (1 (wa g1)))) pu)"),
        ("(((h2 h2) (g2 (1 (wb g2)))) pv)", "(((@A_zs *) (g2 (1 (wb g2)))) pv)"),
        ("@mg_lf = (((x ar) (y qr)) (((bh x) (qh y)) ((bh ar) (qh qr))))",
         "@mg_lf = ((ca (y qr)) ((cb (qh y)) (cc (qh qr))))\n  & @fan ~ (ca (cb cc))"),
        ("@dz_leaf = ((((0 *) ch) ((0 *) pr)) (b ((b ch) pr)))", "@dz_leaf = ((c ((0 *) pr)) (b ((b (1 (c (0 *)))) pr)))"),
    ]
    for a, b in rep:
        assert a in core, a
        core = core.replace(a, b.replace("\\n", "\n"))
    return core + FAN


BAL = r"""
// ---- bl: list of channel-likes -> one balanced fan tree (pairing passes, pipelined; paid once, not per round)
@bl = ((?((@bl_nil @bl_c) (pl o)) pl) o)
@bl_nil = (* (@A_zs *))
@bl_c = (* ((a rest) o))
  & rest ~ (t2 pl2)
  & t2 ~ ?((@bl_one @bl_more) (pl2 (a o)))
@bl_one = (* (a a))
@bl_more = (* (pl2 (a o)))
  & @pp ~ ((1 (a (1 pl2))) l2)
  & @bl ~ (l2 o)
// pp: one pairing pass [a b c d e] -> [fan(a,b) fan(c,d) e]
@pp = ((?((@pp_nil @pp_c1) (pl o)) pl) o)
@pp_nil = (* (0 *))
@pp_c1 = (* ((a rest) o))
  & rest ~ (t2 pl2)
  & t2 ~ ?((@pp_one @pp_two) (pl2 (a o)))
@pp_one = (* (a (1 (a (0 *)))))
@pp_two = (* ((b rest) (a (1 (c o2)))))
  & @fan ~ (a (b c))
  & @pp ~ (rest o2)
"""


def bal_variant(core):
    """Channel ends gathered as difference lists (as in the list variant), then turned once per vertex into a balanced
    tree of fan processes: per LP round a vertex of degree d pays ~log2(d) fan levels."""
    a = "@dz_leaf = ((((0 *) ch) ((0 *) pr)) (b ((b ch) pr)))"
    assert a in core
    return core.replace(a, "@dz_leaf = ((((0 *) cl) ((0 *) pr)) (b ((b (1 (c (0 *)))) pr)))\n  & @bl ~ (cl c)") + FAN + BAL


def build(k=2, variant="list"):
    core = {"list": CORE, "fan": fan_variant(CORE), "bal": bal_variant(CORE)}[variant]
    return core + cc_pipe("A", "mx", 0, k=k) + tl_leafmap("A", "  & y ~ x\n  & i ~ *") + lib()


if __name__ == "__main__":
    for v in ("list", "fan", "bal"):
        open(os.path.join(ROOT, "runs", "exp16", f"recon_{v}.hvm"), "w").write(build(2, v))
    print("wrote runs/exp16/recon_{list,fan,bal}.hvm")
