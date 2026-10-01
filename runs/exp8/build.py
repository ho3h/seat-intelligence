"""exp8: 8 NEW graph programs composed ONLY from genome/lib/graphprims.py primitives plus glue (@prog root, walker
step/fin bodies, small leaf bodies). usage: python3 runs/exp8/build.py [prog|all]  -> runs/exp8/<prog>.hvm
Each program function below is the whole authoring effort for that program (its line count is reported)."""
import sys, os, inspect
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

K = 16  # walker lookahead
UND_STEP = """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 0) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 0) g3))))"""  # undirected unweighted edge -> two pushes (weight 0)


def t5_cluster_label():
    b = Book(); G.lg(b); G.relax(b, "cc"); G.adjacency(b); G.const_trie(b, "gl_inf", "16777215")
    G.iota_trie(b, "io"); G.to_list(b, "tl"); G.stream(b, "w", K, UND_STEP, "((* g) g)")
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* (0 *)) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @gl_inf ~ (L3 D0)
  & @io ~ (L4 (0 C0))
  & @cc_loop ~ ((G (D0 (C0 (L5 16777215)))) D)
  & @tl ~ (D (L6 (0 (n ((0 *) out)))))
""")
    return b


def t5_reconcile_canon():
    b = Book(); G.lg(b); G.relax(b, "mx", maximize=True); G.adjacency(b); G.const_trie(b, "z0", "0")
    G.iota_trie(b, "io"); G.to_list(b, "tl")
    G.stream(b, "w", K, """((L (T g)) ((u (v s)) (L3 (T3 g3))))
  & L ~ {L1 {L2 L3}}
  & T ~ {T1 T3}
  & T1 ~ $([>] $(s gt))
  & gt ~ $([^] $(1 ok))
  & ok ~ {k1 k2}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 k1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 k2) g3))))""", "((* (* g)) g)")
    b.add("""
@prog = ((n (tau es)) out)
  & n ~ ?(((* (* (0 *))) @p_pos) (tau (es out)))
@p_pos = (nm1 (tau (es out)))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 (tau G0)) G))
  & @z0 ~ (L3 D0)
  & @io ~ (L4 (0 C0))
  & @mx_loop ~ ((G (D0 (C0 (L5 0)))) D)
  & @tl ~ (D (L6 (0 (n ((0 *) out)))))
""")
    return b


def t5_cluster_members_of():
    b = Book(); G.lg(b); G.sssp(b, "sp"); G.adjacency(b); G.stream(b, "w", K, UND_STEP, "((* g) g)")
    G.filter_list(b, "fl", """(x (i (n f)))
  & i ~ $([<] $(n a))
  & x ~ $([<] $(16777215 r))
  & a ~ $([&] $(r f))""")
    b.add("""
@prog = ((n (x es)) out)
  & n ~ {n0 {n1 n2}}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (x (L3 (16777215 (G D)))))
  & @fl ~ (D (L4 (0 (n2 ((0 *) out)))))
""")
    return b


def t3_cc_largest():
    b = Book(); G.lg(b); G.relax(b, "cc"); G.adjacency(b); G.const_trie(b, "gl_inf", "16777215")
    G.iota_trie(b, "io"); G.const_trie(b, "z0", "0"); G.update(b, "hadd", "add")
    G.scatter(b, "sc", "hadd", "(x (i (n (x a))))\n  & i ~ $([<] $(n a))")
    G.reduce(b, "mx", "(x x)", "max"); G.stream(b, "w", K, UND_STEP, "((* g) g)")
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* 0) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 {L7 {L8 L9}}}}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @gl_inf ~ (L3 D0)
  & @io ~ (L4 (0 C0))
  & @cc_loop ~ ((G (D0 (C0 (L5 16777215)))) D)
  & @z0 ~ (L6 H0)
  & @sc ~ (D (L7 (0 ((L8 n) (H0 H)))))
  & @mx ~ (H (L9 out))
""")
    return b


def t3_wsp_dist():
    b = Book(); G.lg(b); G.sssp(b, "sp"); G.adjacency(b); G.get(b, "gt"); G._sel(b)
    G.stream(b, "w", K, """((L g) ((u (v w)) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & w ~ {w1 w2}
  & @gl_adj ~ (g (u1 (L1 ((v1 w1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 w2) g3))))""", "((* g) g)")
    b.add("""
@prog = ((n (s (t es))) out)
  & n ~ ?(((* (* (* 16777215))) @p_pos) (s (t (es out))))
@p_pos = (nm1 (s (t (es out))))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & n ~ {n1 n2}
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (s (L3 (16777215 (G D)))))
  & t ~ {t1 t2}
  & t1 ~ $([<] $(n2 tin))
  & tin ~ {ti1 ti2}
  & t2 ~ $([*] $(ti1 key))
  & @gt ~ (D (key (L4 got)))
  & ti2 ~ ?(((* 16777215) @gl_sel2) (got out))
""")
    return b


def _c_walker(b):
    """shared glue for T5 (c, ...) programs: walk c, set C[i] = c_i, count n; L arrives later through a DUP chain."""
    G.update(b, "cset", "set")
    G.stream(b, "cw", K, """((i (Lw T)) (x (i2 (Lw2 T2))))
  & i ~ {i1 ix}
  & ix ~ $([+1] i2)
  & Lw ~ {L1 Lw2}
  & @cset ~ (T (i1 (L1 (x T2))))""", "((n (* T)) (n T))")


def t5_prop_conflict_keys():
    b = Book(); G.lg(b); G.const_trie(b, "z0", "0"); G.const_trie(b, "zz", "(0 0)"); _c_walker(b)
    G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver(b, "dv")
    G.update(b, "zu", """((s val) (v o))
  & s ~ ?((@d_first @d_more) (val (v o)))""")
    b.add("""
@d_first = (* (v (1 v)))
@d_more = (sm1 (val (v (s2 vb))))
  & val ~ {va vb}
  & va ~ $([!] $(v ne))
  & ne ~ $([*] $(2 ne2))
  & sm1 ~ $([+1] s1)
  & s1 ~ $([|] $(ne2 s2))
@ck_no = (* (t t))
@ck_yes = (* (i (t (1 ((a c) t)))))
  & i ~ {i1 i2}
  & i1 ~ $([>>] $(2 a))
  & i2 ~ $([&] $(3 c))
""")
    G.fold(b, "ck", """(x (i (acc o)))
  & x ~ (s *)
  & s ~ $([>] $(1 f))
  & f ~ ?((@ck_no @ck_yes) (i (acc o)))""", idx=True, env=False)
    G.stream(b, "aw", K, """((A (B (Q Z))) ((x (k v)) (A2 (B2 (Q2 Z2)))))
  & A ~ {A1 A2}
  & B ~ {B1 B2}
  & @rq ~ (Q (x (A1 (r Q2))))
  & r ~ $([*] $(4 r4))
  & r4 ~ $([+] $(k key))
  & @zu ~ (Z (key (B1 (v Z2))))""", "((* (* (Q Z))) (Q Z))")
    b.add("""
@prog = ((c at) out)
  & @cw_blk ~ (c ((0 (Lw C0)) (n C)))
  & n ~ {n1 n2}
  & n1 ~ $([>] $(0 pos))
  & n2 ~ $([-] $(pos nm1))
  & @lg ~ (nm1 L)
  & L ~ {Lw {L1 {L2 {L3 {L4 Lz}}}}}
  & @z0 ~ (L1 C0)
  & @zq ~ (L2 Q0)
  & Lz ~ $([+] $(2 Lzz))
  & Lzz ~ {Z1 {Z2 {Z3 Z4}}}
  & @zz ~ (Z1 Z0)
  & @aw_blk ~ (at ((L3 (Z2 (Q0 Z0))) (Q Z)))
  & @dv ~ (C (Q L4))
  & @ck ~ (Z (Z3 (0 ((0 *) out))))
  & Z4 ~ *
""")
    return b


def t5_rewrite_neighbours():
    b = Book(); G.lg(b); G.const_trie(b, "z0", "0"); _c_walker(b)
    G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver(b, "dv"); G.update(b, "bor", "or")
    G.filter_list(b, "fl", "(x (* (* x)))")
    G.stream(b, "ew", K, """((A (Kk (Q B))) ((u v) (A5 (K3 (Q2 B2)))))
  & A ~ {A1 {A2 {A3 {A4 A5}}}}
  & Kk ~ {K1 {K2 K3}}
  & @rq ~ (Q (u (A1 (ru Qa))))
  & @rq ~ (Qa (v (A2 (rv Q2))))
  & ru ~ {ru1 ru2}
  & rv ~ {rv1 rv2}
  & ru1 ~ $([=] $(K1 eu))
  & rv1 ~ $([=] $(K2 ev))
  & eu ~ {eu1 eu2}
  & ev ~ {ev1 ev2}
  & eu1 ~ $([>] $(ev1 fu))
  & ev2 ~ $([>] $(eu2 fv))
  & @bor ~ (B (rv2 (A3 (fu B1))))
  & @bor ~ (B1 (ru2 (A4 (fv B2))))""", "((* (* (Q B))) (Q B))")
    b.add("""
@prog = ((k (c es)) out)
  & @cw_blk ~ (c ((0 (Lw C0)) (n C)))
  & n ~ {n1 n2}
  & n1 ~ $([>] $(0 pos))
  & n2 ~ $([-] $(pos nm1))
  & @lg ~ (nm1 L)
  & L ~ {Lw {L1 {L2 {L3 {L4 {L5 {L6 L7}}}}}}}
  & @z0 ~ (L1 C0)
  & @zq ~ (L2 Q0)
  & @z0 ~ (L3 B0)
  & @ew_blk ~ (es ((L4 (k (Q0 B0))) (Q B)))
  & @dv ~ (C (Q L5))
  & @fl ~ (B (L6 (0 (* ((0 *) out)))))
  & L7 ~ *
""")
    return b


KC_ACT = """(K (d (c (d2 (f m)))))
  & d ~ {d1 dx}
  & d1 ~ $([=] $(16777215 dead))
  & dead ~ ?((@kc_alive @kc_dead) (K (dx (c (d2 (f m))))))"""


def t3_kcore_size():
    b = Book(); G.lg(b); G.adjacency(b); G.const_trie(b, "z0", "0"); G.update(b, "dinc", "inc"); G._sel(b)
    G.frontier(b, "kc", KC_ACT, "(* (* 1))", "add", "0")
    b.add("""
@kc_dead = (* (* (x (* (x (0 0))))))
@kc_alive = (K (d (c (d2 (die 0)))))
  & d ~ $([-] $(c nd))
  & nd ~ {nd1 nd2}
  & nd1 ~ $([<] $(K dd))
  & dd ~ {die1 die}
  & die1 ~ ?((@gl_sel1 @gl_sel2s) (nd2 (16777215 d2)))
""")
    G.reduce(b, "al", """(x (i (n o)))
  & i ~ $([<] $(n a))
  & x ~ $([<] $(16777215 r))
  & a ~ $([&] $(r o))""", "+", idx=True, env=True)
    G.stream(b, "w", K, """((L (g h)) ((u v) (L5 (g3 h3))))
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & u ~ {u1 {u2 u3}}
  & v ~ {v1 {v2 v3}}
  & @gl_adj ~ (g (u1 (L1 ((v1 0) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 0) g3))))
  & @dinc ~ (h (u3 (L3 (* h2))))
  & @dinc ~ (h2 (v3 (L4 (* h3))))""", "((* gh) gh)")
    b.add("""
@prog = ((n (k es)) out)
  & n ~ ?(((* (* 0)) @p_pos) (k (es out)))
@p_pos = (nm1 (k (es out)))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @gl_zl ~ (L1 G0)
  & @z0 ~ (L2 H0)
  & @w_blk ~ (es ((L3 (G0 H0)) (G H)))
  & @z0 ~ (L4 C0)
  & @kc_loop ~ ((G (H (C0 (L5 k)))) D)
  & @al ~ (D (L6 (0 (n out))))
""")
    return b


def t3_degrees():
    b = Book(); G.lg(b); G.const_trie(b, "z0", "0"); G.update(b, "dinc", "inc"); G.to_list(b, "tl")
    G.stream(b, "w", K, """((L h) ((u v) (L3 h2)))
  & L ~ {L1 {L2 L3}}
  & @dinc ~ (h (u (L1 (* h1))))
  & @dinc ~ (h1 (v (L2 (* h2))))""", "((* h) h)")
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* (0 *)) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 L3}}
  & @z0 ~ (L1 H0)
  & @w_blk ~ (es ((L2 H0) H))
  & @tl ~ (H (L3 (0 (n ((0 *) out)))))
""")
    return b


# two-colouring = min-propagation of d = 2*label + parity with message d^1 (frontier + the library RELAX act);
# a component is bipartite iff no edge has d[u] == d[v] at the fixpoint (checked by multicast lookups per edge).
BIP_STEP = """((L (g (q h))) ((u v) (L7 (g3 (q2 h2)))))
  & L ~ {L1 {L2 {L3 {L4 {L5 L7}}}}}
  & u ~ {u1 {u2 u3}}
  & v ~ {v1 {v2 v3}}
  & @gl_adj ~ (g (u1 (L1 ((v1 0) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 0) g3))))
  & @rq ~ (q (u3 (L3 (ru q1))))
  & @rq ~ (q1 (v3 (L4 (rv q2))))
  & ru ~ {ru1 ru2}
  & ru1 ~ $([=] $(rv bad))
  & @bor ~ (h (KEY (L5 (bad h2))))"""


def _bip_common(b):
    G.lg(b); G.adjacency(b); G.const_trie(b, "gl_inf", "16777215"); G.const_trie(b, "z0", "0"); G._sel(b)
    G.iota_trie(b, "io"); G.zip2(b, "dbl", "(x (y o))\n  & x ~ $([+] $(y o))")
    G.frontier(b, "tc", G.RELAX, "(m (* r))\n  & m ~ $([^] $(1 r))", "min", "16777215")
    G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver_keep(b, "dvk"); G.update(b, "bor", "or")


BIP_PROG = """
@prog = ((n es) out)
  & n ~ ?(((* ZERO) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 {L7 {L8 {L9 {L10 L11}}}}}}}}}}
  & @gl_zl ~ (L1 G0)
  & @zq ~ (L2 Q0)
  & @z0 ~ (L3 B0)
  & @w_blk ~ (es ((L4 (G0 (Q0 B0))) (G (Q B))))
  & @gl_inf ~ (L5 D0)
  & @io ~ (L6 (0 Ia))
  & @io ~ (L7 (0 Ib))
  & @dbl ~ (Ia (Ib (L8 C0)))
  & @tc_loop ~ ((G (D0 (C0 (L9 16777215)))) D)
  & @dvk ~ (D (Q (L10 D2)))
"""


def t3_two_colour():
    b = Book(); _bip_common(b)
    G.stream(b, "w", K, BIP_STEP.replace("KEY", "u3x").replace("u ~ {u1 {u2 u3}}", "u ~ {u1 {u2 {u3 u3x}}}")
             .replace("ru ~ {ru1 ru2}\n  & ", "ru ~ {ru1 *}\n  & "), "((* gqh) gqh)")
    G.reduce(b, "anyb", "(x x)", "|")
    G.fold(b, "col", """(x (i ((n bad) (acc o))))
  & i ~ $([<] $(n keep))
  & x ~ $([&] $(1 p))
  & bad ~ $([*] $(16777215 bm))
  & p ~ $([|] $(bm v))
  & keep ~ ?((@col_drop @col_keep) (v (acc o)))""")
    b.add("@col_drop = (* (t t))\n@col_keep = (* (x (t (1 (x t)))))")
    b.add(BIP_PROG.replace("ZERO", "(0 *)") + """  & n ~ {n1 n2}
  & @anyb ~ (B (L11 bad))
  & @col ~ (D2 (Lc (0 ((n1 bad) ((0 *) out)))))
  & n2 ~ *
""")
    b.defs["p_pos"] = b.defs["p_pos"].replace("{L10 L11}", "{L10 {L11 Lc}}")
    return b


def t3_bipartite_comps():
    b = Book(); _bip_common(b)
    G.stream(b, "w", K, BIP_STEP.replace("KEY", "rk").replace("ru ~ {ru1 ru2}", "ru ~ {ru1 ru2}\n  & ru2 ~ $([>>] $(1 rk))"),
             "((* gqh) gqh)")
    G.zip2(b, "pr", "(x (y (x y)))")
    G.reduce(b, "cnt", """((d bad) (i (n o)))
  & i ~ {i1 {i2 i3}}
  & i1 ~ $([<] $(n inr))
  & i2 ~ $([+] $(i3 twoi))
  & d ~ $([=] $(twoi root))
  & bad ~ $([=] $(0 ok))
  & root ~ $([&] $(ok r2))
  & inr ~ $([&] $(r2 o))""", "+", idx=True, env=True)
    b.add(BIP_PROG.replace("ZERO", "0") + """  & @pr ~ (D2 (B (L11 Z)))
  & @cnt ~ (Z (Lc (0 (n o2))))
  & out ~ o2
""")
    b.defs["p_pos"] = b.defs["p_pos"].replace("{L10 L11}", "{L10 {L11 Lc}}")
    return b


# ---- batched reachability: sources are processed in batches of 24 (one bit each in a 24-bit mask); batch b runs
# its own frontier (masks OR-propagated forward along edges) on its own copy of the adjacency trie; all batches in
# parallel. D[(b << L) | v] = mask of the batch-b sources that reach v by a path of length >= 1.
REACH_ACT = """(* (d (c (d2 (f m)))))
  & d ~ {dA dB}
  & dA ~ $([|] $(c nw))
  & nw ~ {nw1 {d2 m}}
  & nw1 ~ $([!] $(dB f))"""
REACH_STEP = """((A (Bw (Cw (G C)))) ((s w) (A2 (Bw2 (Cw2 (G2 C2))))))
  & A ~ {A1 A2}
  & Bw ~ {B1 {B2 Bw2}}
  & Cw ~ {C1 Cw2}
  & s ~ {s1 {s2 s3}}
  & w ~ {w1 w2}
  & @bc ~ (G (A1 ((B1 (s1 (w1 0))) G2)))
  & s2 ~ $([/] $(24 sb))
  & sb ~ $([<<] $(B2 sbs))
  & sbs ~ $([|] $(w2 key))
  & s3 ~ $([%] $(24 sm))
  & 1 ~ $([<<] $(sm bit))
  & @cor ~ (C (key (C1 (bit C2))))"""
REACH_PROG = """
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & n ~ {n1 n2}
  & @lg ~ (c L)
  & n1 ~ $([+] $(23 nb))
  & nb ~ $([/] $(24 B))
  & B ~ $([-] $(1 Bm1))
  & @lg ~ (Bm1 Lb)
  & Lb ~ {Lb1 {Lb2 Lb4}}
  & L ~ {L1 {L2 {L3 L4}}}
  & Lb4 ~ $([+] $(L4 Lc))
  & Lc ~ {Lc1 {Lc2 {Lc3 Lc4}}}
  & @gl_zl ~ (Lc1 G0)
  & @z0 ~ (Lc2 C0)
  & @w_blk ~ (es ((Lb1 (L1 (Lc3 (G0 C0)))) (G C)))
  & @pb ~ (G (C (Lb2 (L2 D))))
"""
# leaf test "bit v of D[v // 24 batch] is set" on the combined trie index j = (b << L) | v; env (n L)
SELF_BIT = """  & j ~ {j1 j2}
  & L ~ {La Lb}
  & j1 ~ $([>>] $(La bb))
  & bb ~ {b1 b2}
  & b1 ~ $([<<] $(Lb bs))
  & j2 ~ $([-] $(bs v))
  & v ~ {v1 {v2 v3}}
  & v1 ~ $([<] $(n inr))
  & v2 ~ $([/] $(24 vb))
  & vb ~ $([=] $(b2 same))
  & v3 ~ $([%] $(24 vm))
  & xs ~ $([>>] $(vm xt))
  & xt ~ $([&] $(1 bit))
  & inr ~ $([&] $(same t1))
  & t1 ~ $([&] $(bit cyc))"""


def _reach_common(b):
    G.lg(b); G.adjacency(b); G.const_trie(b, "z0", "0"); G.update(b, "cor", "or"); G.bcast(b, "bc", "gl_adj")
    G.frontier(b, "rb", REACH_ACT, "(m (* m))", "or", "0")
    G.zip2e(b, "pb", "(g (c (Li o)))\n  & Li ~ {L1 L2}\n  & @z0 ~ (L1 D0)\n  & @rb_loop ~ ((g (D0 (c (L2 0)))) o)")
    G.stream(b, "w", K, REACH_STEP, "((* (* (* gc))) gc)")


def t3_cyclic_vertices():
    b = Book(); _reach_common(b)
    G.reduce(b, "cy", "(xs (j ((n L) cyc)))\n" + SELF_BIT, "+", idx=True, env=True)
    b.add("@prog = ((n es) out)\n  & n ~ ?(((* 0) @p_pos) (es out))" + REACH_PROG + "  & @cy ~ (D (Lc4 (0 ((n2 L3) out))))")
    return b


def t3_closure_size():
    b = Book(); _reach_common(b)
    G.reduce(b, "cl", "(x0 (j ((n L) o)))\n  & x0 ~ {x xs}\n" + SELF_BIT + "\n"
             + G.POP24.replace("ud ~ $([&] $(255 o))", "ud ~ $([&] $(255 pc))") + "\n  & pc ~ $([-] $(cyc o))",
             "+", idx=True, env=True)
    b.add("@prog = ((n es) out)\n  & n ~ ?(((* 0) @p_pos) (es out))" + REACH_PROG + "  & @cl ~ (D (Lc4 (0 ((n2 L3) out))))")
    return b


def t3_reach_queries():
    b = Book(); _reach_common(b); G.mc_empty(b, "zq"); G.mc_request(b, "rq"); G.mc_deliver(b, "dv")
    G.stream(b, "qw", K, """((A (Bs (q h))) ((a bq) (A2 (Bs2 (q2 h2)))))
  & A ~ {A1 A2}
  & Bs ~ {B1 Bs2}
  & a ~ {a1 {a2 a3}}
  & bq ~ {b1 b2}
  & a1 ~ $([/] $(24 ab))
  & ab ~ $([<<] $(B1 abs))
  & abs ~ $([|] $(b1 key))
  & @rq ~ (q (key (A1 (r q2))))
  & a2 ~ $([%] $(24 am))
  & r ~ $([>>] $(am rs))
  & rs ~ $([&] $(1 bit))
  & a3 ~ $([=] $(b2 eq))
  & eq ~ $([|] $(bit ans))
  & h ~ (1 (ans h2))""", "((* (* (q h))) q)\n  & h ~ (0 *)")
    b.add("@prog = ((n (qs es)) out)\n  & n ~ ?(((* (* (0 *))) @p_pos) (qs (es out)))"
          + REACH_PROG.replace("(nm1 (es out))", "(nm1 (qs (es out)))").replace("{Lc3 Lc4}", "{Lc3 {Lc4 {Lc5 Lc6}}}")
          + "  & @zq ~ (Lc4 Q0)\n  & @qw_blk ~ (qs ((Lc5 (L3 (Q0 out))) Q))\n  & @dv ~ (D (Q Lc6))\n  & n2 ~ *")
    return b


# lexicographically smallest topological order is sequential by nature (Kahn with a min-heap): one iteration per
# output vertex; each iteration = min-reduce over the in-degree trie (kept), remove v, peek v's out-list, and stream
# the list decrementing in-degrees. The adjacency and in-degree tries are built in parallel while reading the edges.
TOPO_BODY = """((E (k (I (G h)))) ((E4 (k4 (I3 (G2 h2)))) go))
  & E ~ {E1 {E2 {E3 {E5 E4}}}}
  & E1 ~ (L1 n1)
  & E2 ~ (L2 *)
  & E3 ~ (L3 *)
  & E5 ~ (L4 n2)
  & @mr ~ (I (L1 (0 (n1 (I1 v)))))
  & v ~ {v1 {v2 v3}}
  & @rm ~ (I1 (v1 (L2 (* I2))))
  & @pk ~ (G (v2 (L3 (lst G2))))
  & @dw_blk ~ (lst ((L4 I2) I3))
  & h ~ (1 (v3 h2))
  & k ~ $([+1] kk)
  & kk ~ {k3 k4}
  & k3 ~ $([<] $(n2 go))"""


def t3_topo_order():
    b = Book(); G.lg(b); G.adjacency(b); G.const_trie(b, "z0", "0"); G.update(b, "dinc", "inc"); G._sel(b)
    G.update(b, "rm", "(* (* 16777215))"); G.update(b, "pk", "peek"); G.update(b, "dd", "dec")
    G.mapreduce(b, "mr", """(x (i (n (x2 r))))
  & x ~ {x1 x2}
  & x1 ~ $([=] $(0 z))
  & i ~ {i1 i2}
  & i1 ~ $([<] $(n inr))
  & z ~ $([&] $(inr ok))
  & ok ~ ?(((* 16777215) @gl_sel2) (i2 r))""", "min")
    G.stream(b, "dw", K, "((L I) ((w *) (L2 I2)))\n  & L ~ {L1 L2}\n  & @dd ~ (I (w (L1 (* I2))))", "((* I) I)")
    G.iterate(b, "tp", TOPO_BODY)
    G.stream(b, "w", K, """((L (g h)) ((u v) (L4 (g2 h2))))
  & L ~ {L1 {L2 L4}}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u (L1 ((v1 0) g2))))
  & @dinc ~ (h (v2 (L2 (* h2))))""", "((* gh) gh)")
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* (0 *)) @p_pos) (es out))
@p_pos = (nm1 (es out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gl_zl ~ (L1 G0)
  & @z0 ~ (L2 H0)
  & @w_blk ~ (es ((L3 (G0 H0)) (G H)))
  & @tp_it ~ (((L4 n) (0 (H (G out)))) (* (* (* (* (0 *))))))
""")
    return b


PROGS = {f.__name__: f for f in [t3_cc_largest, t3_degrees, t3_two_colour, t3_bipartite_comps, t3_cyclic_vertices,
                                 t3_closure_size, t3_reach_queries, t3_topo_order]}
# built before the coordinator restricted this experiment to t3_a (other agents own t3_b / t5): kept as extra evidence
EXTRAS = {f.__name__: f for f in [t5_cluster_label, t5_reconcile_canon, t5_cluster_members_of, t3_wsp_dist,
                                  t5_prop_conflict_keys, t5_rewrite_neighbours, t3_kcore_size]}


def glue_lines(f):
    src = inspect.getsource(f)
    return len([l for l in src.splitlines()[1:] if l.strip() and not l.strip().startswith("#") and "return b" not in l])


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, f in {**PROGS, **EXTRAS}.items():
        if which not in ("all", name) and not (which == "main" and name in PROGS): continue
        b = f(); path = os.path.join(D, name + ".hvm")
        open(path, "w").write(f"// {name} (exp8): composed from genome/lib/graphprims.py by runs/exp8/build.py\n" + b.text())
        nd, nl = b.size()
        print(f"{name:26s} composition lines {glue_lines(f):3d}   emitted net: {nd} defs, {nl} lines")
