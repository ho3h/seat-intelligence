"""Swing 20, end-to-end net ("full"): LP + conflict detection + ordered must-not-link greedy, all in ONE net.

Extends the fan variant of genome/exp16/net.py (read that docstring first) with a second, label-keyed stage:
  * every accepted edge also puts a probe on u, so after LP it knows label(u), and emits the item (u v) into a sparse trie
    keyed by that label (merged up the edge tree, so each label's edge list keeps input order = processing order: the
    encoder lays the edge tree out by descending score, ties ascending (u, v), RECONCILIATION-SPEC step 2);
  * every vertex, after LP, emits (i reply-wire) keyed by its label (merged up the vertex trie);
  * every must-not-link pair found inside one component emits (a b) keyed by that label.
  The three sparse tries are merged (leaf payload = three difference lists: members, edges, pairs). Walking the result:
  a label with no pair replies its label to every member; a label with pairs (a conflicted component) runs the greedy
  of genome/exp16/greedy.py on its members (cells now carry the reply wire) and replies the greedy's labels.
Output (canon, conflicts, skipped): canon after the greedy, the conflicting pairs (a b c) in input order, and the skipped
merges (u v) grouped by component label ascending, processing order within.
"""
from __future__ import annotations
import os, re, sys
from .net import CORE, FAN, fan_variant, cc_pipe, tl_leafmap, lib
from .greedy import NET as GREEDY


def _defs(text, names):
    """Pick whole definitions (with their redex lines) out of a book text."""
    out = []
    for blk in re.split(r"(?m)^(?=@)", text):
        m = re.match(r"@(\w+) =", blk)
        if m and m.group(1) in names: out.append(blk.rstrip() + "\n")
    return "".join(out)


KEEP_CORE = ["pa", "pa_leaf", "pa_node", "pa_L", "pa_R", "mg", "mg_a0", "mg_a1", "mg_b0", "mg_b1", "mg_lf", "mg_nd",
             "dz", "dz_e", "dz_p", "dz_leaf", "dz_node", "sd", "sd_nil", "sd_cons"]
KEEP_GREEDY = ["fold", "f_nil", "f_cons", "ns", "ys", "fd", "fd_leaf", "fd_node", "blk", "bk_nil", "bk_cons", "rlc",
               "rl", "rl_node", "rl_leaf", "rlm", "rm_nil", "rm_cons"]

STAGE = r"""
@prog = ((n (L (tau (E (HE (M HM)))))) (C (F K)))
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 {L7 {L8 {L9 {L10 L11}}}}}}}}}}
  & @ew ~ (HE ((L1 tau) (E (te t2e))))
  & @mw ~ (HM (L2 (M (tm (((0 *) F) t2m)))))
  & @mg ~ (L3 (te (tm T)))
  & @dz ~ (T (L4 (0 (S P))))
  & @A_loop ~ (L5 (S Sf))
  & @pzf ~ (Sf (P (L6 (L7 (0 (S3 t2v))))))
  & @mg2 ~ (L8 (t2e (t2m t2a)))
  & @mg2 ~ (L9 (t2a (t2v T2)))
  & @st ~ (T2 (L10 (0 ((0 *) K))))
  & @A_tl ~ (S3 (L11 (0 (n ((0 *) C)))))

// ---- mg2: merge of stage-2 sparse tries; leaf payload (V (E M)), three difference lists
@mg2 = (L (a (b o)))
  & a ~ (ta pa)
  & ta ~ ?((@mh_a0 @mh_a1) (pa (L (b o))))
@mh_a0 = (* (* (b b)))
@mh_a1 = (* (pa (L (b o))))
  & b ~ (tb pb)
  & tb ~ ?((@mh_b0 @mh_b1) (pa (pb (L o))))
@mh_b0 = (pa (* (* (1 pa))))
@mh_b1 = (* (pa (pb (L (1 po)))))
  & L ~ ?((@mh_lf @mh_nd) (pa (pb po)))
@mh_lf = (((x1 r1) ((x2 r2) (x3 r3))) (((h1 x1) ((h2 x2) (h3 x3))) ((h1 r1) ((h2 r2) (h3 r3)))))
@mh_nd = (lm ((al ar) ((bl br) (ol or))))
  & lm ~ {l1 l2}
  & @mg2 ~ (l1 (al (bl ol)))
  & @mg2 ~ (l2 (ar (br or)))

// ---- edge tree walk: stage-1 trie (channels, probe on u) and stage-2 trie (edge item keyed by label(u))
@ew = (h (K (e (t t2))))
  & h ~ ?((@ew_leaf @ew_node) (K (e (t t2))))
@ew_node = (hm ((L tau) ((el er) (t t2))))
  & hm ~ {h1 h2}
  & L ~ {L1 {L2 {L3 L4}}}
  & tau ~ {t1 tx}
  & @ew ~ (h1 ((L1 t1) (el (tl t2l))))
  & @ew ~ (h2 ((L2 tx) (er (tr t2r))))
  & @mg ~ (L3 (tl (tr t)))
  & @mg2 ~ (L4 (t2l (t2r t2)))
@ew_leaf = ((L tau) ((u (v s)) (t t2)))
  & s ~ $([<] $(tau rej))
  & rej ~ ?((@ew_acc @ew_rej) (L (u (v (t t2)))))
@ew_rej = (* (* (* (* ((0 *) (0 *))))))
@ew_acc = (L (u (v (t t2))))
  & L ~ {L1 {L2 {L3 L4}}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @pa ~ (u1 (L1 (((c2 c1) (g1 (1 (wu g1)))) pu)))
  & @pa ~ (v1 (L2 (((c1 c2) (q2 q2)) pv)))
  & @mg ~ (L3 (pu (pv t)))
  & @pa ~ (wu (L4 (((e1 e1) ((h (1 ((u2 v2) h))) (q3 q3))) t2)))

// ---- must-not-link walk: probes, conflict list, stage-2 pair items keyed by the shared label
@mw = (h (L (m (t (r t2)))))
  & h ~ ?((@mw_leaf @mw_node) (L (m (t (r t2)))))
@mw_node = (hm (L ((ml mr) (t ((rh rr) t2)))))
  & hm ~ {h1 h2}
  & L ~ {L1 {L2 {L3 L4}}}
  & @mw ~ (h1 (L1 (ml (tl ((x rr) t2l)))))
  & @mw ~ (h2 (L2 (mr (tr ((rh x) t2r)))))
  & @mg ~ (L3 (tl (tr t)))
  & @mg2 ~ (L4 (t2l (t2r t2)))
@mw_leaf = (L ((a (b live)) (t (r t2))))
  & live ~ ?((@mw_dead @mw_live) (L (a (b (t (r t2))))))
@mw_dead = (* (* (* ((0 *) ((q q) (0 *))))))
@mw_live = (* (L (a (b (t ((rh rr) t2))))))
  & L ~ {L1 {L2 {L3 L4}}}
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & @pa ~ (a1 (L1 (((@A_zs *) (g1 (1 (wa g1)))) pu)))
  & @pa ~ (b1 (L2 (((@A_zs *) (g2 (1 (wb g2)))) pv)))
  & @mg ~ (L3 (pu (pv t)))
  & wa ~ {la1 la2}
  & la1 ~ $([=] $(wb eq))
  & eq ~ ?((@mw_ne @mw_eq) (L4 (a2 (b2 (la2 ((rh rr) t2))))))
@mw_ne = (* (* (* (* ((h h) (0 *))))))
@mw_eq = (* (L (a (b (l ((h (1 ((a1 (b1 l1)) h))) t2))))))
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & l ~ {l1 l2}
  & @pa ~ (l2 (L (((e e) ((f f) (g (1 ((a2 b2) g))))) t2)))

// ---- after LP: probes get labels; every vertex emits (i reply) keyed by its label; leaves become (reply 0)
@pzf = (s (p (L (LF (base (o t2))))))
  & L ~ ?((@pzf_leaf @pzf_node) (s (p (LF (base (o t2))))))
@pzf_leaf = ((x *) (pr (LF (b ((r 0) t2)))))
  & @sd ~ (pr (x y))
  & @pa ~ (y (LF (((h (1 ((b r) h))) ((e e) (q q))) t2)))
@pzf_node = (lm ((sa sc) ((qa qc) (LF (base ((oa oc) t2))))))
  & lm ~ {l1 {l2 l3}}
  & LF ~ {F1 {F2 F3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @pzf ~ (sa (qa (l1 (F1 (b1 (oa ta))))))
  & @pzf ~ (sc (qc (l2 (F2 (bR (oc tc))))))
  & @mg2 ~ (F3 (ta (tc t2)))

// ---- stage-2 walk: per label c, reply c (no pair) or run the greedy (pairs); k = difference list of skipped merges
@st = (t (L (base k)))
  & t ~ (tg pl)
  & tg ~ ?((@st_e @st_p) (pl (L (base k))))
@st_e = (* (* (* (h h))))
@st_p = (* (pl (L (base k))))
  & L ~ ?((@st_leaf @st_node) (pl (base k)))
@st_node = (lm ((a c) (base (h r))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @st ~ (a (l1 (b1 (x r))))
  & @st ~ (c (l2 (bR (h x))))
@st_leaf = ((((0 *) vs) (((0 *) es) ((0 *) ms))) (c k))
  & ms ~ (mt mp)
  & mt ~ ?((@st_ok @st_bad) (mp (vs (es (c k)))))
@st_ok = (* (vs (es (c (h h)))))
  & @rep ~ (vs c)
  & es ~ *
@st_bad = (* (mp (vs (es (c k)))))
  & c ~ *
  & @cells ~ (vs (H T))
  & @fold ~ (es (H (T ((1 mp) (K1 (Tf Hf))))))
  & @rpl ~ (Tf Hf)
  & @cat ~ (K1 k)
@rep = ((?((@rp_nil @rp_cons) (pl c)) pl) c)
@rp_nil = (* *)
@rp_cons = (* (((b r) rest) c))
  & c ~ {r c2}
  & b ~ *
  & @rep ~ (rest c2)
// cells: member list [(i reply)] -> perfect tree (height lg(s-1)) of cells (x (c reply)), padding (16777215 (0 *))
@cells = (vs (H T))
  & @len ~ (vs (0 (s vs2)))
  & s ~ $([-] $(1 s1))
  & @lg ~ (s1 Hc)
  & Hc ~ {H1 H}
  & @bt ~ (H1 (vs2 (T rest)))
  & rest ~ *
@len = ((?((@ln_nil @ln_cons) (pl (n (o l2)))) pl) (n (o l2)))
@ln_nil = (* (n (n (0 *))))
@ln_cons = (* ((h t) (n (o (1 (h t2))))))
  & n ~ $([+1] n2)
  & @len ~ (t (n2 (o t2)))
@bt = (H (l (T rest)))
  & H ~ ?((@bt_leaf @bt_node) (l (T rest)))
@bt_node = (hm (l ((a b) rest)))
  & hm ~ {h1 h2}
  & @bt ~ (h1 (l (a mid)))
  & @bt ~ (h2 (mid (b rest)))
@bt_leaf = (l (T rest))
  & l ~ (tg pl)
  & tg ~ ?((@bt_pad @bt_take) (pl (T rest)))
@bt_pad = (* ((16777215 (0 *)) (0 *)))
@bt_take = (* (((x r) t) ((x1 (x2 r)) t)))
  & x ~ {x1 x2}
@rpl = (t H)
  & H ~ ?((@rpl_leaf @rpl_node) t)
@rpl_leaf = (* (c c))
@rpl_node = (hm (l r))
  & hm ~ {h1 h2}
  & @rpl ~ (l h1)
  & @rpl ~ (r h2)
@cat = ((?((@ct_nil @ct_cons) (pl (tail o))) pl) (tail o))
@ct_nil = (* (t t))
@ct_cons = (* ((h t) (tail (1 (h o)))))
  & @cat ~ (t (tail o))
"""


def build(k=2):
    core = _defs(fan_variant(CORE), KEEP_CORE)
    g = _defs(GREEDY, KEEP_GREEDY)
    # greedy cells carry the reply wire: (x c) -> (x (c r))
    for a, b in [("@fd_leaf = ((x c) (u (v ((x3 c3) (cu cv)))))", "@fd_leaf = ((x (c r)) (u (v ((x3 (c3 r)) (cu cv)))))"),
                 ("@rl_leaf = ((x c) (P (x c2)))", "@rl_leaf = ((x (c r)) (P (x (c2 r))))")]:
        assert a in g, a
        g = g.replace(a, b)
    return STAGE + core + FAN + g + cc_pipe("A", "mx", 0, k=k) + tl_leafmap("A", "  & y ~ x\n  & i ~ *") + lib()


if __name__ == "__main__":
    from .net import ROOT
    open(os.path.join(ROOT, "runs", "exp16", "recon_full.hvm"), "w").write(build())
    print("wrote runs/exp16/recon_full.hvm")
