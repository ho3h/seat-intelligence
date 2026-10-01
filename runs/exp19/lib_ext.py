"""GRAPH-SWING-3 template extensions (runs/exp19). Hand-written HVM2 text, nothing learned. Conventions as in
runs/exp5 / runs/exp9: complete binary tries of depth L keyed by vertex id (high bit first); bitsets are word tries of
depth W = lg((n-1)>>4) holding 16-bit words (vertex s at word s>>4, bit s&15)."""


def wpc():
    """@wpc ~ (C (W o)): o = total popcount of the word trie C (needs @pop from runs/exp9 lib_ext.mex()).
    Cost: 2^W x (pop ~13 itrs) + adds; depth ~ 10 + 3W."""
    return """
@wpc = (C (W o))
  & W ~ ?((@wpc_leaf @wpc_node) (C o))
@wpc_leaf = (w o)
  & @pop ~ (w o)
@wpc_node = (wm ((a b) o))
  & wm ~ {w1 w2}
  & @wpc ~ (a (w1 x))
  & @wpc ~ (b (w2 y))
  & x ~ $([+] $(y o))
"""


def wlow():
    """@wlow ~ (A (B (W (base o)))): o = the smallest bit index set in the word-wise AND of word tries A and B
    (16777215 if the AND is empty). base = index of the first bit of the trie (0 at the root). Lowest set bit of a
    word: p = w & -w, then popcount(p - 1) (needs @pop and @min). Cost: 2^W x ~25 itrs; depth ~ 15 + 5W."""
    return """
@wlow = (a (b (W (base o))))
  & W ~ ?((@wlow_leaf @wlow_node) (a (b (base o))))
@wlow_leaf = (a (b (base o)))
  & a ~ $([&] $(b w))
  & w ~ {w1 {w2 w3}}
  & w1 ~ $([=] $(0 z))
  & z ~ ?((@wlow_some @wlow_none) (w2 (w3 (base o))))
@wlow_none = (* (* (* (* 16777215))))
@wlow_some = (w (w2 (base o)))
  & 0 ~ $([-] $(w2 nw))
  & w ~ $([&] $(nw p))
  & p ~ $([-] $(1 q))
  & @pop ~ (q c)
  & base ~ $([+] $(c o))
@wlow_node = (wm ((a1 a2) ((b1 b2) (base o))))
  & wm ~ {w1 {w2 w3}}
  & base ~ {x1 x2}
  & 16 ~ $([<<] $(w3 half))
  & x2 ~ $([+] $(half xR))
  & @wlow ~ (a1 (b1 (w1 (x1 lo))))
  & @wlow ~ (a2 (b2 (w2 (xR hi))))
  & @min ~ (lo (hi o))
"""


def scc_out():
    """Readout of two msbfs final state tries (runs/exp9 msbfs; leaves (R (F X))): A from the forward search (R_v =
    sources that reach v) and B from the search on the reversed graph (R_v = sources reachable from v). The SCC of v is
    A_v & B_v, so its label is the lowest set bit (@wlow).
      @sccl ~ (A (B (L (base ((n W) (tail o))))))   list of labels of vertices < n, in order, prepended to tail
      @sccc ~ (A (B (L (base ((n W) o)))))          number of vertices v < n with label(v) == v (= number of SCCs)
    Cost: one wlow per leaf (2^W words); depth ~ 4L + wlow."""
    return """
@sccl = (a (b (L (base (E (acc o))))))
  & L ~ ?((@sccl_leaf @sccl_node) (a (b (base (E (acc o))))))
@sccl_leaf = ((ra *) ((rb *) (i ((n W) (acc o)))))
  & i ~ $([<] $(n keep))
  & @wlow ~ (ra (rb (W (0 lab))))
  & keep ~ ?((@sccl_drop @sccl_keep) (lab (acc o)))
@sccl_drop = (* (t t))
@sccl_keep = (* (x (t (1 (x t)))))
@sccl_node = (lm ((a1 a2) ((b1 b2) (base (E (acc o))))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {x1 x2}
  & 1 ~ $([<<] $(l3 half))
  & x2 ~ $([+] $(half xR))
  & E ~ {E1 E2}
  & @sccl ~ (a1 (b1 (l1 (x1 (E1 (mid o))))))
  & @sccl ~ (a2 (b2 (l2 (xR (E2 (acc mid))))))
@sccc = (a (b (L (base (E o)))))
  & L ~ ?((@sccc_leaf @sccc_node) (a (b (base (E o)))))
@sccc_leaf = ((ra *) ((rb *) (i ((n W) o))))
  & i ~ {i1 i2}
  & i1 ~ $([<] $(n inr))
  & @wlow ~ (ra (rb (W (0 lab))))
  & lab ~ $([=] $(i2 eq))
  & inr ~ $([&] $(eq o))
@sccc_node = (lm ((a1 a2) ((b1 b2) (base (E o)))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {x1 x2}
  & 1 ~ $([<<] $(l3 half))
  & x2 ~ $([+] $(half xR))
  & E ~ {E1 E2}
  & @sccc ~ (a1 (b1 (l1 (x1 (E1 p)))))
  & @sccc ~ (a2 (b2 (l2 (xR (E2 q)))))
  & p ~ $([+] $(q o))
"""


def euler():
    """Euler tour + pointer jumping over an arc trie (new; for t3_tree_parents). Arc ids: edge i gives arcs 2i = u->v
    and 2i+1 = v->u (twin = a ^ 1). An arc trie of depth La holds packed values nxt*1024 + dist (dist < 1024).
      @fill ~ (L (x t))                     every leaf = x (a number, DUP-copied)
      @vf ~ (G (L (0 ((r (S La)) (N N2)))))  G = vertex trie of out-arc lists [b1..bd]: sets N[b_j ^ 1] = b_{j+1}*1024+1
                                            (cyclic; at the root r the arc b_d ^ 1 gets the sentinel S instead of b1),
                                            i.e. next(a) = the out-arc after twin(a) at a's head: the Euler tour of the
                                            doubled tree starting at r's first out-arc and ending at the sentinel S.
      @pjl ~ (c (P ((La S) Pf)))            c rounds of pointer jumping P[a] := P[nxt(a)] + dist(a), fetched with
                                            multicast requests (@pu/@zq of runs/exp9 mc()) keyed by nxt(a) and delivered
                                            by @dv; arcs already pointing at S are not re-requested (the sentinel
                                            would otherwise collect a long DUP chain). After lg(S+1) rounds
                                            dist(a) = number of tour arcs from a to the end, so a comes before its
                                            twin iff dist(a) > dist(a ^ 1).
      @dv ~ (v (q L))                       multicast delivery (graphprims mc_deliver)
      @cs ~ (t (k (L ((f x) t2))))          conditional set: leaf k := x if f else unchanged
    Cost per jumping round: one traversal + one keyed request per arc not yet at S (~16 itrs/level); depth per round
    ~ 16 La (the request) + DUP chain + O(La); rounds = La (fixed count, no convergence test)."""
    from lib import nav
    return """
@fill = (L (x o))
  & L ~ ?((@fill_leaf @fill_node) (x o))
@fill_leaf = (x x)
@fill_node = (lm (x (a b)))
  & lm ~ {l1 l2}
  & x ~ {x1 x2}
  & @fill ~ (l1 (x1 a))
  & @fill ~ (l2 (x2 b))
@vf = (t (L (base (E (acc o)))))
  & L ~ ?((@vf_leaf @vf_node) (t (base (E (acc o)))))
@vf_leaf = (lst (i ((r (S La)) (acc o))))
  & i ~ $([=] $(r isr))
  & @sl0 ~ (lst (isr (S (La (acc o)))))
@vf_node = (lm ((a c) (base (E (acc o)))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & E ~ {E1 E2}
  & @vf ~ (a (l1 (b1 (E1 (mid o)))))
  & @vf ~ (c (l2 (bR (E2 (acc mid)))))
@sl0 = ((?((@sl0_nil @sl0_cons) (pl (isr (S (La (N o)))))) pl) (isr (S (La (N o)))))
@sl0_nil = (* (* (* (* (N N)))))
@sl0_cons = (* ((b rest) (isr (S (La (N o))))))
  & b ~ {b1 b2}
  & isr ~ ?((@sl_sel1 @sl_sel2s) (b2 (S c)))
  & b1 ~ $([^] $(1 k))
  & @sw ~ (rest (k (c (La (N o)))))
@sl_sel1 = (x (* x))
@sl_sel2s = (* (* (y y)))
@sw = ((?((@sw_nil @sw_cons) (pl (k (c (La (N o)))))) pl) (k (c (La (N o)))))
@sw_nil = (* (k (c (La (N o)))))
  & c ~ $([*] $(1024 c2))
  & c2 ~ $([+] $(1 v))
  & @nset ~ (N (k (La (v o))))
@sw_cons = (* ((b rest) (k (c (La (N o))))))
  & b ~ {b1 b2}
  & b1 ~ $([*] $(1024 v0))
  & v0 ~ $([+] $(1 v))
  & La ~ {La1 La2}
  & @nset ~ (N (k (La1 (v N2))))
  & b2 ~ $([^] $(1 k2))
  & @sw ~ (rest (k2 (c (La2 (N2 o)))))
@nset_act = (* (p p))
@pjl = (c (P (E o)))
  & c ~ ?((@pjl_done @pjl_step) (P (E o)))
@pjl_done = (P (* P))
@pjl_step = (cm (P (E o)))
  & E ~ {E1 {E2 {E3 {E4 E5}}}}
  & E1 ~ (L1 *)
  & @zq ~ (L1 q0)
  & E2 ~ (L2 *)
  & @pjr ~ (L2 (E3 (P (q0 (Pc (Pn q))))))
  & E4 ~ (L4 *)
  & @dv ~ (Pc (q L4))
  & @pjl ~ (cm (Pn (E5 o)))
@pjr = (Lr (E (p (q (pc (pn q2))))))
  & Lr ~ ?((@pjr_leaf @pjr_node) (E (p (q (pc (pn q2))))))
@pjr_leaf = ((La S) (p (q (pc (pn q2)))))
  & p ~ {p1 {p2 pc}}
  & p1 ~ $([>>] $(10 k))
  & k ~ {k1 k2}
  & k1 ~ $([=] $(S at))
  & at ~ ?((@pj_req @pj_stay) (La (k2 (p2 (q (pn q2))))))
@pj_stay = (* (* (* (x (q (x q))))))
@pj_req = (La (k (p (q (pn q2)))))
  & @pu ~ (q (k (La (r q2))))
  & p ~ $([&] $(1023 d))
  & r ~ $([+] $(d pn))
@pjr_node = (lm (E ((pa pb) (q ((ca cb) ((na nb) q2))))))
  & lm ~ {l1 l2}
  & E ~ {E1 E2}
  & @pjr ~ (l1 (E1 (pa (q (ca (na qm))))))
  & @pjr ~ (l2 (E2 (pb (qm (cb (nb q2))))))
@dv = (m (q L))
  & L ~ ?((@dv_leaf @dv_node) (m q))
@dv_leaf = (R (R *))
@dv_node = (lm ((m1 m2) (q1 q2)))
  & lm ~ {l1 l2}
  & @dv ~ (m1 (q1 l1))
  & @dv ~ (m2 (q2 l2))
@cs_act = (old ((f x) new))
  & f ~ ?((@cs_keep @cs_take) (old (x new)))
@cs_keep = (o (* o))
@cs_take = (* (* (x x)))
""" + nav("nset", "nset_act") + nav("cs", "cs_act")
