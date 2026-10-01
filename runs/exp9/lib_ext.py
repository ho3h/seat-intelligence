"""GRAPH-SWING-2 template extensions (runs/exp9). Each function returns hand-written HVM2 text; nothing is learned.
Conventions follow runs/exp5: a trie is a complete binary trie of depth L (keys 0..2^L-1, high bit first, leaves at
depth 0), L is passed as a number and consumed by one SWI per level. Costs are per call, n = number of leaves.
USES counts how many exp9 programs each template served (filled in by hand in docs/GRAPH-SWING-2.md)."""


def get():
    """get(D, k, n, L) -> D[k] if k < n else 16777215; the rest of D is erased.  @get ~ (D (k (n (L o)))).
    getd(D, k, n, L, dflt) is the same with an explicit default: @getd ~ (D (k (n (L (dflt o))))).
    lk(D, k, L) is the unguarded lookup. Cost: L levels x ~6 interactions, depth ~4 per level (siblings erased
    off the critical path)."""
    return """
@get = (D (t (n (L o))))
  & @getd ~ (D (t (n (L (16777215 o)))))
@getd = (D (t (n (L (df o)))))
  & t ~ {t1 t2}
  & t1 ~ $([<] $(n inr))
  & inr ~ ?((@get_out @get_in) (D (t2 (L (df o)))))
@get_out = (* (* (* (df df))))
@get_in = (* (D (t (L (* o)))))
  & @lk ~ (D (t (L o)))
@lk = (D (k (L o)))
  & L ~ ?((@lk_leaf @lk_node) (D (k o)))
@lk_leaf = (x (* x))
@lk_node = (lm (D (k o)))
  & k ~ {k1 k2}
  & lm ~ {l1 l2}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 b))
  & b ~ ?((@lk_L @lk_R) (D (k2 (l2 o))))
@lk_L = ((l *) (k (L o)))
  & @lk ~ (l (k (L o)))
@lk_R = (* ((* r) (k (L o))))
  & @lk ~ (r (k (L o)))
"""


def und_adj(p):
    """Stream step for an undirected weighted edge list into an adjacency trie of (v w) lists (both directions).
    State (L g). Uses @gp (nav push). @<p>_step / @<p>_fin for stream(). Cost: 2 keyed pushes per edge."""
    return f"""
@{p}_step = ((L g) ((u (v w)) (L3 g3)))
  & L ~ {{L1 {{L2 L3}}}}
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & w ~ {{w1 w2}}
  & @gp ~ (g (u1 (L1 ((v1 w1) g2))))
  & @gp ~ (g2 (v2 (L2 ((u2 w2) g3))))
@{p}_fin = ((* g) g)
"""


def mex():
    """mex(a) -> smallest c >= 0 whose bit is clear in the 24-bit mask a. @mex ~ (a o).
    Branch-free: p = ~a & (a+1) isolates the lowest clear bit, then popcount(p-1) by SWAR (3 masks, one multiply).
    Cost: 16 interactions, depth ~12. Also exports @pop (24-bit popcount, 13 interactions, depth ~10)."""
    return """
@mex = (a o)
  & a ~ {a1 a2}
  & a1 ~ $([^] $(16777215 na))
  & a2 ~ $([+1] a3)
  & na ~ $([&] $(a3 p))
  & p ~ $([-] $(1 q))
  & @pop ~ (q o)
@pop = (x o)
  & x ~ {x1 x2}
  & x1 ~ $([>>] $(1 y))
  & y ~ $([&] $(5592405 y2))
  & x2 ~ $([-] $(y2 z))
  & z ~ {z1 z2}
  & z1 ~ $([&] $(3355443 za))
  & z2 ~ $([>>] $(2 zb))
  & zb ~ $([&] $(3355443 zc))
  & za ~ $([+] $(zc w))
  & w ~ {w1 w2}
  & w1 ~ $([>>] $(4 wa))
  & w2 ~ $([+] $(wa wb))
  & wb ~ $([&] $(986895 wc))
  & wc ~ $([*] $(65793 wd))
  & wd ~ $([>>] $(16 o))
"""


def mc():
    """Multicast request trie (exp5 idea 3, packaged). @zq ~ (L Q): empty request trie, every leaf a wire loop (y y) =
    (chain input, chain end). @pu ~ (Q (k (L (x Q2)))): push reply wire x onto chain k (keyed nav update, expands
    before Q exists). Later, whatever is wired into a leaf's chain input is DUP-copied to every pushed x, and the
    chain end yields one more copy (use it as the value itself, or erase it). Cost: one nav (~16 interactions per level)
    per consumer, plus one DUP per consumer when the value flows; value-flow depth = chain length (DUPs in series)."""
    from lib import nav
    return """
@zq = (?(((y y) @zq_node) o) o)
@zq_node = (lm (a b))
  & lm ~ {l1 l2}
  & @zq ~ (l1 a)
  & @zq ~ (l2 b)
@pu_act = ((i o) (x (i o2)))
  & o ~ {x o2}
""" + nav("pu", "pu_act")


def minmax():
    """@min ~ (a (b o)), @max ~ (a (b o)): one compare + one switch selecting a pre-wired operand (sel1/sel2 forms of
    exp5 dag_longest). Cost 6 interactions, depth ~4."""
    return """
@min = (a (b o))
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?((@sel2 @sel1s) (a2 (b2 o)))
@max = (a (b o))
  & a ~ {a1 a2}
  & b ~ {b1 b2}
  & a1 ~ $([<] $(b1 lt))
  & lt ~ ?((@sel1 @sel2s) (a2 (b2 o)))
@sel1 = (x (* x))
@sel2 = (* (y y))
@sel1s = (* (x (* x)))
@sel2s = (* (* (y y)))
"""


def peel():
    """Synchronous peeling loop (k-core style), the exp5 frontier-round skeleton with a "die below threshold" leaf.
    @pl ~ ((G (S (C (L k)))) Sf): G adjacency trie of plain neighbour lists, S state trie (live: current degree,
    dead: 16777215 minus later decrements, i.e. >= 2^23), C decrement trie for this round (all zero initially), L trie depth, k threshold. Returns the
    final state trie. Uses @ad (nav add), @pn (nav push of a plain value), @zt, @cfa (count live leaves, i.e. < 2^23).
    Cost per round: one traversal (~20 interactions per leaf) + one keyed add per edge endpoint of each dying
    vertex; depth per round ~ L*16 (gated emission) + L; rounds = peeling depth + 1."""
    from lib import nav
    return """
@pl = ((g (st (dc E))) o)
  & E ~ {E1 {E2 E3}}
  & E1 ~ (L1 *)
  & @zt ~ (L1 dn)
  & E2 ~ {Ea Eb}
  & Ea ~ (Lr *)
  & @prd ~ (Lr (Eb (g (st (dc (dn (g2 (st2 (dn2 any)))))))))
  & any ~ ?((@pl_done @pl_again) (g2 (st2 (dn2 (E3 o)))))
@pl_done = (* (st (* (* st))))
@pl_again = (* (g (st (dn (E o)))))
  & @pl ~ ((g (st (dn E))) o)
@prd = (L (E (g (st (dc (dn (g2 (st2 (do any)))))))))
  & L ~ ?((@prd_leaf @prd_node) (E (g (st (dc (dn (g2 (st2 (do any)))))))))
@prd_node = (lm (E ((g1 gr) ((s1 sr) ((c1 cr) (dn ((h1 hr) ((e1 er) (do any)))))))))
  & lm ~ {l1 l2}
  & E ~ {Ea Eb}
  & @prd ~ (l1 (Ea (g1 (s1 (c1 (dn (h1 (e1 (dm a1)))))))))
  & @prd ~ (l2 (Eb (gr (sr (cr (dm (hr (er (do a2)))))))))
  & a1 ~ $([|] $(a2 any))
@prd_leaf = (E (g (s (c (dn (g2 (s2 (do any))))))))
  & s ~ $([-] $(c s1))
  & s1 ~ {sa sb}
  & E ~ {Ex Ey}
  & Ey ~ (* k)
  & sa ~ $([<] $(k die))
  & die ~ {d1 {any d3}}
  & d1 ~ ?((@pk_live @pk_die) (sb s2))
  & d3 ~ ?((@pk_quiet @pk_emit) (g (dn (g2 (do Ex)))))
@pk_live = (x x)
@pk_die = (* (* 16777215))
@pk_quiet = (g (dn (g (dn *))))
@pk_emit = (* (g (dn (g2 (do E)))))
  & E ~ (L *)
  & @ed ~ (g (dn (g2 (do L))))
@ed = ((?((@ed_nil @ed_cons) (p (dn (g2 (do L))))) p) (dn (g2 (do L))))
@ed_nil = (* (dn ((0 *) (dn *))))
@ed_cons = (* ((v rest) (dn ((1 (v2 rest2)) (do L)))))
  & v ~ {v1 v2}
  & L ~ {La Lb}
  & @ad ~ (dn (v1 (La (1 dm))))
  & @ed ~ (rest (dm (rest2 (do Lb))))
@ad_act = (old (c o))
  & old ~ $([+] $(c o))
@pn_act = (lst (x (1 (x lst))))
@cfa = (t (L o))
  & L ~ ?((@cfa_leaf @cfa_node) (t o))
@cfa_leaf = (x o)
  & x ~ $([<] $(8388608 o))
@cfa_node = (lm ((a b) o))
  & lm ~ {l1 l2}
  & @cfa ~ (a (l1 x))
  & @cfa ~ (b (l2 y))
  & x ~ $([+] $(y o))
""" + nav("ad", "ad_act") + nav("pn", "pn_act")


def und_nb(p):
    """Stream step: undirected unweighted edge (u v) -> push v onto list u and u onto list v of a neighbour trie (plain
    ids, @pn). State (L g). Cost: 2 keyed pushes per edge."""
    return f"""
@{p}_step = ((L g) ((u v) (L3 g3)))
  & L ~ {{L1 {{L2 L3}}}}
  & u ~ {{u1 u2}}
  & v ~ {{v1 v2}}
  & @pn ~ (g (u1 (L1 (v1 g2))))
  & @pn ~ (g2 (v2 (L2 (u2 g3))))
@{p}_fin = ((* g) g)
"""


def msbfs(girth=False, pop=False):
    """All-sources BFS with bitsets (new). Every vertex v keeps (R F X): R = sources that have reached v, F = sources
    whose BFS frontier is at v (reached exactly last round), X = a per-program accumulator. Sets are word tries (depth
    W = lg((n-1)>>4), 16-bit words, source s at word s>>4, bit s&15). Round k: the gather trie holds, per vertex, ONES
    = OR of the neighbours' frontiers (and, if girth, TWOS = sources seen from >= 2 neighbours). The round traversal
    computes N = ONES & ~R (sources at distance exactly k), R |= N, F = N, calls the program hook
        @xl ~ (k (anyN (odd (even (popN (X (X' cand)))))))
    and, if N is nonzero, pushes N to every neighbour of v in the next gather trie (keyed nav OR-updates, gated
    emission as in the exp5 frontier core). odd = ONES & F_prev (an edge between two vertices at distance k-1: odd
    closed walk 2k-1), even = TWOS & N (two distinct predecessors: closed walk 2k); both only when girth=True.
    popN only when pop=True. Loop while some N != 0 and every cand == 16777215. Round 0 seeds ONES(v) = {v}.
    Entry: @ml ~ ((G (S0 (T0 (L (W 0))))) (Sfinal cand)) with (S0 T0) from @zs0 ~ (L (W (0 (S0 T0)))).
    Cost per round: n leaves x (2^W words x ~12 interactions) + for each vertex with a nonzero frontier, one keyed
    OR-update per incident arc (nav ~16/level + 2^W words). Depth per round ~ 16L + 4W + popcount/flag reductions;
    rounds = max eccentricity + 1 (or first cycle for girth). Needs @pn/@zt/@zl/@lg (exp5 trie + peel())."""
    from lib import nav
    # word-level zip: N = o & ~r, R2 = r | o, an = OR N, od = OR (o & f), ev = OR (t & N), pp = sum pop(N)
    nd = ["N", "an"] + (["n2"] if girth else []) + (["n3"] if pop else [])
    def dupn(ws):
        t = ws[-1]
        for w in reversed(ws[:-1]): t = "{" + w + " " + t + "}"
        return t
    wl = ["@wz_leaf = (r (f (o (t (R2 (N (an (od (ev pp)))))))))",
          "  & r ~ {r1 r2}", "  & r1 ~ $([^] $(65535 nr))",
          "  & o ~ {o1 {o2 o3}}" if girth else "  & o ~ {o1 o2}",
          "  & o1 ~ $([&] $(nr n0))", "  & r2 ~ $([|] $(o2 R2))", f"  & n0 ~ {dupn(nd)}"]
    if girth: wl += ["  & o3 ~ $([&] $(f od))", "  & t ~ $([&] $(n2 ev))"]
    else: wl += ["  & f ~ *", "  & t ~ *", "  & od ~ 0", "  & ev ~ 0"]
    wl += ["  & @pop ~ (n3 pp)"] if pop else ["  & pp ~ 0"]
    if girth:
        wa_leaf = """@wa_leaf = (o (t (x (O2 T2))))
  & o ~ {o1 o2}
  & x ~ {x1 x2}
  & o1 ~ $([|] $(x1 O2))
  & o2 ~ $([&] $(x2 a))
  & t ~ $([|] $(a T2))"""
    else:
        wa_leaf = """@wa_leaf = (o (t (x (O2 t))))
  & o ~ $([|] $(x O2))"""
    return "\n".join(wl) + """
@wz = (W (R (F (O (T o)))))
  & W ~ ?((@wz_leaf @wz_node) (R (F (O (T o)))))
@wz_node = (wm ((ra rb) ((fa fb) ((oa ob) ((ta tb) ((Ra Rb) ((Na Nb) (an (od (ev pp))))))))))
  & wm ~ {w1 w2}
  & @wz ~ (w1 (ra (fa (oa (ta (Ra (Na (a1 (d1 (e1 p1))))))))))
  & @wz ~ (w2 (rb (fb (ob (tb (Rb (Nb (a2 (d2 (e2 p2))))))))))
  & a1 ~ $([|] $(a2 an))
  & d1 ~ $([|] $(d2 od))
  & e1 ~ $([|] $(e2 ev))
  & p1 ~ $([+] $(p2 pp))
""" + wa_leaf + """
@wa = (W (O (T (x o))))
  & W ~ ?((@wa_leaf @wa_node) (O (T (x o))))
@wa_node = (wm ((oa ob) ((ta tb) ((xa xb) ((Oa Ob) (Ta Tb))))))
  & wm ~ {w1 w2}
  & @wa ~ (w1 (oa (ta (xa (Oa Ta)))))
  & @wa ~ (w2 (ob (tb (xb (Ob Tb)))))
@ga_act = ((O T) ((W x) (O2 T2)))
  & @wa ~ (W (O (T (x (O2 T2)))))
// un(W, j, b): word trie with only bit b of word j set
@un = (W (j (b o)))
  & W ~ ?((@un_leaf @un_node) (j (b o)))
@un_leaf = (* (b o))
  & 1 ~ $([<<] $(b o))
@un_node = (wm (j (b o)))
  & j ~ {j1 j2}
  & wm ~ {w1 {w2 w3}}
  & j1 ~ $([>>] $(w1 sh))
  & sh ~ $([&] $(1 bit))
  & bit ~ ?((@un_L @un_R) (j2 (b (w2 (w3 o)))))
@un_L = (j (b (w (wz (x y)))))
  & @un ~ (w (j (b x)))
  & @zt ~ (wz y)
@un_R = (* (j (b (w (wz (x y))))))
  & @zt ~ (wz x)
  & @un ~ (w (j (b y)))
// zs0(L, W, base) -> (state trie of (0 (0 0)), gather trie of ({v} 0))
@zs0 = (L (W (base (s g))))
  & L ~ ?((@zs0_leaf @zs0_node) (W (base (s g))))
@zs0_leaf = (W (v ((z1 (z2 0)) (u z3))))
  & W ~ {w1 {w2 {w3 w4}}}
  & @zt ~ (w1 z1)
  & @zt ~ (w2 z2)
  & @zt ~ (w3 z3)
  & v ~ {v1 v2}
  & v1 ~ $([>>] $(4 j))
  & v2 ~ $([&] $(15 b))
  & @un ~ (w4 (j (b u)))
@zs0_node = (lm (W (base ((sa sb) (ga gb)))))
  & lm ~ {l1 {l2 l3}}
  & W ~ {w1 w2}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @zs0 ~ (l1 (w1 (b1 (sa ga))))
  & @zs0 ~ (l2 (w2 (bR (sb gb))))
// zg(L, W): gather trie of (0 0) word-trie pairs
@zg = (L (W o))
  & L ~ ?((@zg_leaf @zg_node) (W o))
@zg_leaf = (W (a b))
  & W ~ {w1 w2}
  & @zt ~ (w1 a)
  & @zt ~ (w2 b)
@zg_node = (lm (W (a b)))
  & lm ~ {l1 l2}
  & W ~ {w1 w2}
  & @zg ~ (l1 (w1 a))
  & @zg ~ (l2 (w2 b))
// ml: the round loop. E = (L (W k))
@ml = ((g (st (gt E))) o)
  & E ~ {E1 {E2 E3}}
  & E1 ~ (L1 (W1 *))
  & @zg ~ (L1 (W1 gn))
  & E2 ~ {Ea Eb}
  & Ea ~ (Lr *)
  & @mr ~ (Lr (Eb (g (st (gt (gn (g2 (st2 (gn2 (any cand))))))))))
  & cand ~ {c1 c2}
  & c1 ~ $([=] $(16777215 ci))
  & any ~ $([&] $(ci go))
  & go ~ ?((@ml_done @ml_again) (g2 (st2 (gn2 (E3 (c2 o))))))
@ml_done = (* (st (* (* (c (st c))))))
@ml_again = (* (g (st (gn ((L (W k)) (* o))))))
  & k ~ $([+1] k1)
  & @ml ~ ((g (st (gn (L (W k1))))) o)
@mr = (L (E (g (st (gt (gn (g2 (st2 (go (any cand))))))))))
  & L ~ ?((@mr_leaf @mr_node) (E (g (st (gt (gn (g2 (st2 (go (any cand))))))))))
@mr_node = (lm (E ((g1 gr) ((s1 sr) ((t1 tr) (gn ((h1 hr) ((e1 er) (go (any cand))))))))))
  & lm ~ {l1 l2}
  & E ~ {Ea Eb}
  & @mr ~ (l1 (Ea (g1 (s1 (t1 (gn (h1 (e1 (gm (a1 c1))))))))))
  & @mr ~ (l2 (Eb (gr (sr (tr (gm (hr (er (go (a2 c2))))))))))
  & a1 ~ $([|] $(a2 any))
  & @min ~ (c1 (c2 cand))
@mr_leaf = (E (g ((R (F X)) ((O T) (gn (g2 ((R2 (Ns X2)) (go (any cand)))))))))
  & E ~ {Ex {Ey Ez}}
  & Ey ~ (* (W1 *))
  & Ez ~ (* (* k))
  & @wz ~ (W1 (R (F (O (T (R2 (N (an (od (ev pp))))))))))
  & N ~ {Ns Ne}
  & an ~ $([!] $(0 anb))
  & anb ~ {a1 {any a3}}
  & @xl ~ (k (a1 (od (ev (pp (X (X2 cand)))))))
  & a3 ~ ?((@mq @mm) (g (Ne (gn (g2 (go Ex))))))
@mq = (g (* (gn (g (gn *)))))
@mm = (* (g (N (gn (g2 (go E))))))
  & E ~ (L (W *))
  & @me ~ (g (N (gn (g2 (go (L W))))))
@me = ((?((@me_nil @me_cons) (p (N (gn (g2 (go LW)))))) p) (N (gn (g2 (go LW)))))
@me_nil = (* (* (gn ((0 *) (gn *)))))
@me_cons = (* ((v rest) (N (gn ((1 (v2 rest2)) (go LW))))))
  & v ~ {v1 v2}
  & N ~ {N1 N2}
  & LW ~ {LW1 LW2}
  & LW1 ~ (L W)
  & @ga ~ (gn (v1 (L ((W N1) gm))))
  & @me ~ (rest (N2 (gm (rest2 (go LW2)))))
// sx(st, L): trie of the X accumulators
@sx = (t (L o))
  & L ~ ?((@sx_leaf @sx_node) (t o))
@sx_leaf = ((* (* x)) x)
@sx_node = (lm ((a b) (x y)))
  & lm ~ {l1 l2}
  & @sx ~ (a (l1 x))
  & @sx ~ (b (l2 y))
""" + nav("ga", "ga_act") + (mex() if pop else "") + minmax()


def bitrows():
    """Adjacency bit-matrix (exp5 triangle_count's rows, packaged) plus word-trie utilities.
    @zm ~ (L (W M)): zero matrix, a depth-L trie of depth-W word tries (16-bit words).
    @sb ~ (M (u (L ((v W) M2)))): set bit v of row u (two nested keyed nav updates: row u, then word v>>4).
    @wor ~ (W (a (b o))): word-trie OR.  @wan ~ (W (a (r o))): a & ~r word-wise.
    @wbits ~ (C (W (0 (tail o)))): the set bits of word trie C as an ascending list prepended to tail (tail
    threaded right to left, so all cells are built in parallel; 16-bit words split in halves 16/8/4/2/1).
    Cost: sb ~ (L+W)*16 interactions; wor/wan ~ 2^W * 4; wbits ~ 2^W * 31 * 6."""
    from lib import nav
    return """
@sb_act = (row ((v W) o))
  & v ~ {v1 v2}
  & v1 ~ $([>>] $(4 kw))
  & v2 ~ $([&] $(15 bi))
  & 1 ~ $([<<] $(bi mask))
  & @sr ~ (row (kw (W (mask o))))
@sr_act = (w (mask o))
  & w ~ $([|] $(mask o))
@zm = (L (W o))
  & L ~ ?((@zm_leaf @zm_node) (W o))
@zm_leaf = (W o)
  & @zt ~ (W o)
@zm_node = (lm (W (a b)))
  & lm ~ {l1 l2}
  & W ~ {w1 w2}
  & @zm ~ (l1 (w1 a))
  & @zm ~ (l2 (w2 b))
@wor = (W (a (b o)))
  & W ~ ?((@wor_leaf @wor_node) (a (b o)))
@wor_leaf = (a (b o))
  & a ~ $([|] $(b o))
@wor_node = (wm ((a1 a2) ((b1 b2) (x y))))
  & wm ~ {w1 w2}
  & @wor ~ (w1 (a1 (b1 x)))
  & @wor ~ (w2 (a2 (b2 y)))
@wan = (W (a (r o)))
  & W ~ ?((@wan_leaf @wan_node) (a (r o)))
@wan_leaf = (a (r o))
  & r ~ $([^] $(65535 nr))
  & a ~ $([&] $(nr o))
@wan_node = (wm ((a1 a2) ((b1 b2) (x y))))
  & wm ~ {w1 w2}
  & @wan ~ (w1 (a1 (b1 x)))
  & @wan ~ (w2 (a2 (b2 y)))
@wbits = (C (W (base (tail o))))
  & W ~ ?((@wbits_leaf @wbits_node) (C (base (tail o))))
@wbits_leaf = (w (base (tail o)))
  & @wb ~ (w (base (16 (tail o))))
@wbits_node = (wm ((a b) (base (tail o))))
  & wm ~ {w1 {w2 w3}}
  & base ~ {b1 b2}
  & 16 ~ $([<<] $(w3 half))
  & b2 ~ $([+] $(half bR))
  & @wbits ~ (a (w1 (b1 (mid o))))
  & @wbits ~ (b (w2 (bR (tail mid))))
@wb = (w (base (width (tail o))))
  & width ~ {wd1 wd2}
  & wd1 ~ $([=] $(1 one))
  & one ~ ?((@wb_split @wb_one) (w (base (wd2 (tail o)))))
@wb_one = (* (w (base (* (tail o)))))
  & w ~ ?((@wb_skip @wb_take) (base (tail o)))
@wb_skip = (* (t t))
@wb_take = (* (b (t (1 (b t)))))
@wb_split = (w (base (width (tail o))))
  & width ~ $([>>] $(1 h))
  & h ~ {h1 {h2 {h3 {h4 h5}}}}
  & w ~ {wa wb}
  & 1 ~ $([<<] $(h1 m1))
  & m1 ~ $([-] $(1 mask))
  & wa ~ $([&] $(mask lo))
  & wb ~ $([>>] $(h2 hi))
  & base ~ {b1 b2}
  & b2 ~ $([+] $(h3 bh))
  & @wb ~ (lo (b1 (h4 (mid o))))
  & @wb ~ (hi (bh (h5 (tail mid))))
""" + nav("sb", "sb_act") + nav("sr", "sr_act")


def rounds():
    """Fixed-count ungated push rounds (new): @wr ~ (k (G (C (L o)))) applies k times
        C'[v] = OP over arcs u -> v of f(C[u], w)       (G: trie of adjacency lists)
    with every vertex pushing every round (no gating, no convergence test), so round r+1's control flow never waits
    for round r's data. The leaf emission is the hook @re_emit ~ (lst (c (z (lst2 (zo Lf))))) (walk each list cell,
    keyed update into z, rebuild the list); the fresh accumulator trie comes from @re_zero ~ (L z).
    Cost per round: one traversal (~12 interactions per leaf) + one keyed update per arc (~16 per level).
    Depth: structure ~O(L) per round, data ~(in-degree chain + out-degree DUP chain) per round."""
    return """
@wr = (k (G (C (L o))))
  & k ~ ?((@wr_done @wr_step) (G (C (L o))))
@wr_done = (* (C (* C)))
@wr_step = (km (G (C (L o))))
  & L ~ {L1 {L2 {L3 L4}}}
  & @re_zero ~ (L1 z)
  & @ws ~ (L2 (L3 (G (C (z (G2 C2))))))
  & @wr ~ (km (G2 (C2 (L4 o))))
@ws = (Lr (Lf (g (c (z (g2 zo))))))
  & Lr ~ ?((@ws_leaf @ws_node) (Lf (g (c (z (g2 zo))))))
@ws_leaf = (Lf (lst (cv (z (lst2 zo)))))
  & @re_emit ~ (lst (cv (z (lst2 (zo Lf)))))
@ws_node = (lm (Lf ((ga gb) ((ca cb) (z ((ha hb) zo))))))
  & lm ~ {l1 l2}
  & Lf ~ {f1 f2}
  & @ws ~ (l1 (f1 (ga (ca (z (ha zm))))))
  & @ws ~ (l2 (f2 (gb (cb (zm (hb zo))))))
"""


def prim(second=False):
    """Prim over tries (new). K = trie of (packed adjacency) leaves, packed = key*128 + parent (unreached 8388607,
    visited 16777215; needs n <= 128, w <= 1000). One step: argmin traversal (@am, rebuilds K and returns
    (min packed, index)), one keyed nav on the winner that marks it visited AND hands out its adjacency list (@tk),
    then one keyed guarded-min update per incident arc (@ku; visited leaves are never lowered, and the update returns
    the leaf's visited flag through its payload). A new root starts when the minimum is unreached (key counts 0).
    @prim ~ (c (K (M (L ((tot best) o))))) runs c steps; o = (tot best).
    second=True also keeps, for every vertex v, its ANCESTOR row R_v[a] = max edge weight on the tree path v..a for
    tree ancestors a, 16777215 for non-ancestors (R_v = max(key_v, R_parent), R_v[v] = 0; matrix trie M, @co copies
    a row out, @stn stores one). For an arc from v to an already-visited x that is not v's parent (a non-tree edge),
    maxpath(v, x) = min_a max(R_v[a], R_x[a]) (the minimum is reached at the LCA: rows are INF off the ancestor
    chain and grow going up), and best = min(best, w - maxpath).
    Cost per step: ~20n interactions for the argmin scan + keyed navs; second adds O(n) per incident arc (row copy +
    zip). Depth per step ~ 5L (argmin) + ~2 x 8L (two dependent keyed navs on K) ~ 150; steps = n."""
    from lib import nav
    s = """
@prim = (c (K (M (L (acc o)))))
  & c ~ ?((@pr_done @pr_step) (K (M (L (acc o)))))
@pr_done = (* (* (* (a a))))
@pr_step = (cm (K (M (L ((tot best) o)))))
  & L ~ {L1 {L2 {L3 {L4 {L5 {L6 L7}}}}}}
  & @am2 ~ (K (L1 (0 (K2 (mn (v (lst (16777215 (0 *)))))))))
  & L2 ~ *
  & mn ~ {mn1 {mn2 mn3}}
  & mn1 ~ $([>>] $(7 key0))
  & mn3 ~ $([<] $(8388607 reached))
  & key0 ~ $([*] $(reached key))
  & mn2 ~ $([&] $(127 p))
  & key ~ {k1 k2}
  & v ~ {v1 {v2 {v3 v4}}}
  & p ~ {p1 p2}
  & v1 ~ *
  & tot ~ $([+] $(k2 tot2))
"""
    if second:
        s += """  & @co ~ (M (p1 (L3 (rp M1))))
  & @rm ~ (rp (L4 (0 ((v2 k1) rv))))
  & rv ~ {rv1 rv2}
  & @stn ~ (M1 (v3 (L5 (rv1 M2))))
  & @nb ~ (lst (K2 (M2 (rv2 ((v4 (p2 L6)) (K3 (M3 cm2)))))))
  & @min ~ (best (cm2 best2))
  & @prim ~ (cm (K3 (M3 (L7 ((tot2 best2) o)))))
"""
    else:
        s += """  & k1 ~ *
  & p1 ~ *
  & v2 ~ *
  & v3 ~ *
  & L3 ~ *
  & L4 ~ *
  & L5 ~ *
  & @nb ~ (lst (K2 (M (* ((v4 (p2 L6)) (K3 (M3 *)))))))
  & @prim ~ (cm (K3 (M3 (L7 ((tot2 best) o)))))
"""
    s += """
// am(K, L, base) -> (K' (min packed, index)); ties go left
@am = (t (L (base o)))
  & L ~ ?((@am_leaf @am_node) (t (base o)))
@am_leaf = ((pk l) (i ((p1 l) (p2 i))))
  & pk ~ {p1 p2}
@am_node = (lm ((a b) (base ((ta tb) m))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @am ~ (a (l1 (b1 (ta ma))))
  & @am ~ (b (l2 (bR (tb mb))))
  & @amsel ~ (ma (mb m))
@amsel = ((ma ia) ((mb ib) o))
  & ma ~ {ma1 ma2}
  & mb ~ {mb1 mb2}
  & mb1 ~ $([<] $(ma1 lt))
  & lt ~ ?((@as_l @as_r) ((ma2 ia) ((mb2 ib) o)))
@as_l = (a (* a))
@as_r = (* (* (b b)))
// am2(K, L, base) -> (K' offer): single-pass argmin that also TAKES the winner. Each leaf offers
// (packed (index (list R))) upward, R being a wire back to the leaf's slot in K'. At a node the loser's R is closed
// with its own (packed list) and only the winner travels on; the caller closes the root winner's R with
// (16777215 Nil): the winner is marked visited and its adjacency list handed out, no second keyed descent.
@am2 = (t (L (base o)))
  & L ~ ?((@am2_leaf @am2_node) (t (base o)))
@am2_leaf = ((pk l) (i (X (pk (i (l X))))))
@am2_node = (lm ((a b) (base ((ta tb) o))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @am2 ~ (a (l1 (b1 (ta oa))))
  & @am2 ~ (b (l2 (bR (tb ob))))
  & @amsel2 ~ (oa (ob o))
@amsel2 = ((ma A) ((mb B) o))
  & ma ~ {ma1 ma2}
  & mb ~ {mb1 mb2}
  & mb1 ~ $([<] $(ma1 lt))
  & lt ~ ?((@as2_l @as2_r) ((ma2 A) ((mb2 B) o)))
@as2_l = (A ((mb (* (lb (mb lb)))) A))
@as2_r = (* ((ma (* (la (ma la)))) (B B)))
// ku: guarded min of a packed candidate into a leaf; payload (c vis) returns vis = (leaf was visited)
@ku_act = ((pk l) ((c vis) (pk2 l)))
  & pk ~ {p1 p2}
  & p1 ~ $([=] $(16777215 vi))
  & vi ~ {vis v2}
  & v2 ~ ?((@ku_min @ku_keep) (p2 (c pk2)))
@ku_min = (pk (c o))
  & @min ~ (pk (c o))
@ku_keep = (* (pk (* pk)))
// nb(adjacency list of v, K, M, R_v, S = (v (p L))) -> (K' (M' best candidate))
@nb = ((?((@nb_nil @nb_cons) (pl (K (M (rv (S o)))))) pl) (K (M (rv (S o)))))
@nb_nil = (* (K (M (* (* (K (M 16777215)))))))
@nb_cons = (* (((x w) rest) (K (M (rv (S (K2 (M2 cm))))))))
  & S ~ {S1 {S2 S3}}
  & S1 ~ (v1 (p1 La))
  & x ~ {x1 {x2 {x3 x4}}}
  & w ~ {w1 w2}
  & w1 ~ $([*] $(128 w8))
  & w8 ~ $([+] $(v1 c))
  & @ku ~ (K (x1 (La ((c vis) Km))))
  & x2 ~ $([!] $(p1 np))
  & vis ~ $([&] $(np test))
  & S2 ~ (* (* Lb))
  & Lb ~ {Lb1 Lb2}
"""
    if second:
        s += """  & @co ~ (M (x3 (Lb1 (rx Mm))))
  & rv ~ {r1 r2}
  & test ~ ?((@nb_no @nb_yes) (r1 (rx (w2 (Lb2 cd)))))
  & x4 ~ *
  & @nb ~ (rest (Km (Mm (r2 (S3 (K2 (M2 cr)))))))
  & @min ~ (cd (cr cm))
@nb_no = (* (* (* (* 16777215))))
@nb_yes = (* (ra (rb (w (L c)))))
  & @mm ~ (ra (rb (L m)))
  & w ~ $([-] $(m c))
// rm(R_p, L, base, (v key)) -> R_v
@rm = (r (L (base (vk o))))
  & L ~ ?((@rm_leaf @rm_node) (r (base (vk o))))
@rm_leaf = (x (i ((v k) o)))
  & i ~ $([=] $(v eq))
  & eq ~ ?((@rm_max @rm_zero) (x (k o)))
@rm_max = (x (k o))
  & @max ~ (x (k o))
@rm_zero = (* (* (* 0)))
@rm_node = (lm ((a b) (base (vk (x y)))))
  & lm ~ {l1 {l2 l3}}
  & base ~ {b1 b2}
  & vk ~ {vk1 vk2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @rm ~ (a (l1 (b1 (vk1 x))))
  & @rm ~ (b (l2 (bR (vk2 y))))
// mm(A, B, L) = min over leaves of max(a, b)
@mm = (a (b (L o)))
  & L ~ ?((@mm_leaf @mm_node) (a (b o)))
@mm_leaf = (a (b o))
  & @max ~ (a (b o))
@mm_node = (lm ((a1 a2) ((b1 b2) o)))
  & lm ~ {l1 l2}
  & @mm ~ (a1 (b1 (l1 x)))
  & @mm ~ (a2 (b2 (l2 y)))
  & @min ~ (x (y o))
@co_act = (row (o r2))
  & row ~ {o r2}
""" + nav("co", "co_act") + zrows()
    else:
        s += """  & x3 ~ *
  & x4 ~ *
  & w2 ~ *
  & Lb1 ~ *
  & Lb2 ~ *
  & test ~ *
  & rv ~ *
  & @nb ~ (rest (Km (M (* (S3 (K2 (M2 cm)))))))
"""
    return s + nav("ku", "ku_act") + minmax()


def vfront():
    """All-sources distance vectors by frontier rounds (new; the msbfs skeleton with number vectors instead of
    bitsets). Every vertex v keeps D_v[t] = best known distance v -> t (a depth-L trie of numbers). Round: the
    gather trie holds, per vertex, the componentwise min of the candidate vectors pushed to it; the traversal sets
    N = min(G, D), and if some entry improved, pushes N + w (saturating at 16777215) to every predecessor u of an
    arc u -> v (keyed nav update whose act is a componentwise min, depth-L vector zip). Loop while anything improved.
    Entry: @vl ~ ((R (S0 (G0 (L b)))) Sf) with R = trie of predecessor lists (u w), S0 all-INF vectors, G0 = the
    seed vectors (0 at v). Cost per round: n x 2^L leaf ops (~10 each) + for every improved vertex one keyed update
    per incoming arc plus a 2^L vector zip; depth per round ~ 16L + 6L; rounds = max hop count of a shortest path+1."""
    from lib import nav
    return """
@vl = ((g (st (gt E))) o)
  & E ~ {E1 {E2 E3}}
  & E1 ~ (L1 *)
  & @zv ~ (L1 (L1b gn))
  & L1b ~ *
  & E2 ~ {Ea Eb}
  & Ea ~ (Lr *)
  & @vr ~ (Lr (Eb (g (st (gt (gn (g2 (st2 (gn2 any)))))))))
  & any ~ ?((@vl_done @vl_again) (g2 (st2 (gn2 (E3 o)))))
@vl_done = (* (st (* (* st))))
@vl_again = (* (g (st (gn (E o)))))
  & @vl ~ ((g (st (gn E))) o)
// zv(L, _): trie of all-INF vectors
@zv = (L (x o))
  & x ~ *
  & L ~ {L1 L2}
  & @zm2 ~ (L1 (L2 o))
@zm2 = (L (W o))
  & L ~ ?((@zm2_leaf @zm2_node) (W o))
@zm2_leaf = (W o)
  & @zi ~ (W o)
@zm2_node = (lm (W (a b)))
  & lm ~ {l1 l2}
  & W ~ {w1 w2}
  & @zm2 ~ (l1 (w1 a))
  & @zm2 ~ (l2 (w2 b))
@vr = (L (E (g (st (gt (gn (g2 (st2 (go any)))))))))
  & L ~ ?((@vr_leaf @vr_node) (E (g (st (gt (gn (g2 (st2 (go any)))))))))
@vr_node = (lm (E ((g1 gr) ((s1 sr) ((t1 tr) (gn ((h1 hr) ((e1 er) (go any)))))))))
  & lm ~ {l1 l2}
  & E ~ {Ea Eb}
  & @vr ~ (l1 (Ea (g1 (s1 (t1 (gn (h1 (e1 (gm a1)))))))))
  & @vr ~ (l2 (Eb (gr (sr (tr (gm (hr (er (go a2)))))))))
  & a1 ~ $([|] $(a2 any))
@vr_leaf = (E (g (d (G (gn (g2 (N1 (go any))))))))
  & E ~ {Ex Ey}
  & Ey ~ (L1 *)
  & @vz ~ (L1 (G (d (N ch))))
  & N ~ {N1 N2}
  & ch ~ {any c2}
  & c2 ~ ?((@vq @vm) (g (N2 (gn (g2 (go Ex))))))
@vq = (g (* (gn (g (gn *)))))
@vm = (* (g (N (gn (g2 (go E))))))
  & E ~ (L *)
  & @vem ~ (g (N (gn (g2 (go L)))))
// vz(L, G, D) -> (min(G, D), OR (G < D))
@vz = (L (g (d o)))
  & L ~ ?((@vz_leaf @vz_node) (g (d o)))
@vz_leaf = (g (d (n c)))
  & g ~ {g1 g2}
  & d ~ {d1 d2}
  & g1 ~ $([<] $(d1 c))
  & @min ~ (g2 (d2 n))
@vz_node = (lm ((ga gb) ((da db) ((na nb) c))))
  & lm ~ {l1 l2}
  & @vz ~ (l1 (ga (da (na c1))))
  & @vz ~ (l2 (gb (db (nb c2))))
  & c1 ~ $([|] $(c2 c))
// vem: push N + w to every predecessor (u w) in the list
@vem = ((?((@vem_nil @vem_cons) (p (N (gn (g2 (go L)))))) p) (N (gn (g2 (go L)))))
@vem_nil = (* (* (gn ((0 *) (gn *)))))
@vem_cons = (* (((u w) rest) (N (gn ((1 ((u2 w2) rest2)) (go L))))))
  & u ~ {u1 u2}
  & w ~ {w1 w2}
  & N ~ {N1 N2}
  & L ~ {La {Lb Lc}}
  & @vmu ~ (gn (u1 (La ((Lb (w1 N1)) gm))))
  & @vem ~ (rest (N2 (gm (rest2 (go Lc)))))
@vmu_act = (old ((L (w v)) new))
  & @vadd ~ (L (old (w (v new))))
// vadd(L, old, w, v) -> componentwise min(old, sat(v + w))
@vadd = (L (a (w (v o))))
  & L ~ ?((@vadd_leaf @vadd_node) (a (w (v o))))
@vadd_leaf = (a (w (v o)))
  & v ~ {v1 v2}
  & v1 ~ $([+] $(w s))
  & v2 ~ $([>>] $(23 hi))
  & hi ~ $([*] $(16777215 msk))
  & s ~ $([|] $(msk c))
  & @min ~ (a (c o))
@vadd_node = (lm ((a1 a2) (w ((v1 v2) (x y)))))
  & lm ~ {l1 l2}
  & w ~ {w1 w2}
  & @vadd ~ (l1 (a1 (w1 (v1 x))))
  & @vadd ~ (l2 (a2 (w2 (v2 y))))
""" + nav("vmu", "vmu_act")


def zrows():
    """@zr ~ (L (Lw (base M))): matrix trie whose row u is 0 at u and 16777215 elsewhere (unit distance rows), built
    with one keyed set per row (@stn, nav set). Cost: n x (2^Lw + 16 Lw) interactions, depth ~ 16 Lw + L."""
    from lib import nav
    return """
// zr(L, Lw, base): matrix of rows; row u = 0 at u, 16777215 elsewhere
@zr = (L (Lw (base o)))
  & L ~ ?((@zr_leaf @zr_node) (Lw (base o)))
@zr_leaf = (Lw (u o))
  & Lw ~ {w1 w2}
  & @zi ~ (w1 z)
  & @stn ~ (z (u (w2 (0 o))))
@zr_node = (lm (Lw (base (x y))))
  & lm ~ {l1 {l2 l3}}
  & Lw ~ {w1 w2}
  & base ~ {b1 b2}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @zr ~ (l1 (w1 (b1 x)))
  & @zr ~ (l2 (w2 (bR y)))
@stn_act = (* (x x))
""" + nav("stn", "stn_act")
