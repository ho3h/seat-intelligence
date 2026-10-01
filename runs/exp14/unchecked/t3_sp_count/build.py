"""Build sp_count: count shortest paths from s to t in a directed graph."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book, INF

K = 16  # walker lookahead

DIR_STEP = """((L g) ((u v) (L2 g2)))
  & L ~ {L1 L2}
  & @gl_adj ~ (g (u (L1 ((v 0) g2))))"""


def build_sp_count():
    """Count shortest paths from s to t.

    The key insight: run SSSP but pack both distance AND count into state.
    State = (distance, count)
    Message = (distance+1, count)
    Receiver: if incoming_distance matches my distance, add count
    """
    b = Book()

    # Primitives for building graph
    G.lg(b)
    G.const_trie(b, "z0", "(0 *)")
    G.adjacency(b)
    G.stream(b, "w", K, DIR_STEP, "((* h) h)")

    # Now we'll use frontier but with custom act and combiner for (distance, count) states
    # Initial state: (0, 1) at s, (INF, 0) elsewhere
    G.const_trie(b, "z_inf", "(16777215 (0 *))")  # (INF, 0) for all leaves
    G.update(b, "set_src", "set")  # to set source state to (0, 1)

    # Define the path counting act
    # State d = (distance (count *))
    # Message c = (distance (count *))
    # Output: d2 = new state, f = flag, m = message
    b.add("""
@pc_act = (b (d (c (d2 (f m)))))
  & d ~ (dd (dc *))
  & c ~ (cd (cc *))
  & cd ~ $([<] $(dd lt))
  & lt ~ ?(((@pc_lt @pc_ge) (b (d (c (d2 (f m))))))))

@pc_lt = (b (d (c ((cd (cc *)) (1 (cd (cc *)))))))

@pc_ge = (b (d (c (d2 (f m)))))
  & d ~ (dd (dc *))
  & c ~ (cd (cc *))
  & cd ~ $([-] $(dd equ))
  & equ ~ ?(((@pc_ne @pc_eq) (b (d (c (d2 (f m))))))))

@pc_ne = (b (d (c ((dd (dc *)) (0 (dd (dc *)))))))

@pc_eq = (b (d (c (d2 (f m)))))
  & d ~ (dd (dc *))
  & c ~ (cd (cc *))
  & dc ~ $([+] $(cc nc))
  & nc ~ {nc1 nc2}
  & ((dd (nc1 *)) (1 (dd (nc2 *))) m) ~ ((d2 (f m)))
""")

    # Combiner for path counts with distance checking
    # Receives (d (c *)) pairs, combines by keeping min distance or summing counts
    b.add("""
@pc_comb_act = (l (msg l2))
  & l ~ (ld (lc *))
  & msg ~ (md (mc *))
  & md ~ $([<] $(ld mlt))
  & mlt ~ ?(((@pc_comb_lt @pc_comb_ge) (l (msg l2))))

@pc_comb_lt = (l (msg ((md (mc *)) *)))

@pc_comb_ge = (l (msg (l2 *)))
  & l ~ (ld (lc *))
  & msg ~ (md (mc *))
  & md ~ $([-] $(ld meq))
  & meq ~ ?(((@pc_comb_ne @pc_comb_eq) (l (msg l2))))

@pc_comb_ne = (l (msg ((ld (lc *)) *)))

@pc_comb_eq = (l (msg l2))
  & l ~ (ld (lc *))
  & msg ~ (md (mc *))
  & lc ~ $([+] $(mc sc))
  & l2 ~ (ld (sc *))
""")

    # Message generation: send (distance+1, count)
    b.add("""
@pc_msg = (m (w r))
  & m ~ (d (c *))
  & d ~ $([+] $(1 d1))
  & r ~ (d1 (c *))
""")

    # Now define frontier for path counting
    b.add("""
@pc_loop = ((g (dt (c E))) o)
  & E ~ {E1 {E2 E3}}
  & E1 ~ (L1 *)
  & @pc_zi ~ (L1 ci)
  & E2 ~ {Ea Eb}
  & Ea ~ (Lr *)
  & @pc_rd ~ (Lr (Eb (g (dt (c (ci (g2 (dt2 (co any)))))))))
  & any ~ ?((0 1) (g2 (dt2 (co (E3 o)))))

@pc_zi = (?(((16777215 (0 *)) @pc_zi_n) o) o)
@pc_zi_n = (lm (a c))
  & lm ~ {l1 l2}
  & @pc_zi ~ (l1 a)
  & @pc_zi ~ (l2 c)

@pc_rd = (L (E (g (dt (c (ci (g2 (dt2 (co any)))))))))
  & L ~ ?((@pc_leaf @pc_node) (E (g (dt (c (ci (g2 (dt2 (co any)))))))))

@pc_node = (lm (E ((g1 gr) ((d1 dr) ((c1 cr) (ci ((h1 hr) ((e1 er) (co any)))))))))
  & lm ~ {l1 l2}
  & E ~ {Ea Eb}
  & @pc_rd ~ (l1 (Ea (g1 (d1 (c1 (ci (h1 (e1 (cm a1)))))))))
  & @pc_rd ~ (l2 (Eb (gr (dr (cr (cm (hr (er (co a2)))))))))
  & a1 ~ $([|] $(a2 any))

@pc_leaf = (E (g (d (c (ci (g2 (d2 (co any))))))))
  & E ~ {Ex Ey}
  & Ey ~ (* X)
  & @pc_act ~ (X (d (c (d2 (f m)))))
  & f ~ {any f3}
  & f3 ~ ?((0 1) (g (m (ci (g2 (co Ex))))))
""")

    # Root program
    b.add("""
@prog = ((n (s (t es))) out)
  & n ~ ?(((* (1 *)) @p_pos) ((s (t es)) out))

@p_pos = (nm1 ((s (t es)) out))
  & nm1 ~ {a c}
  & a ~ $([+1] n)
  & @lg ~ (c L)
  & L ~ {L1 {L2 {L3 {L4 {L5 L6}}}}}
  & @z0 ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @z_inf ~ (L3 D0)
  & L4 ~ {L4a L4b}
  & @set_src ~ (D0 (s (L4a ((0 (1 *)) D1))))
  & @z_inf ~ (L4b C0)
  & @pc_loop ~ ((G (D1 (C0 (L5 (16777215 *))))) D2)
  & D2 ~ (d *)
  & d ~ (dist (cnt *))
  & @gv_pc ~ (cnt (t (L6 out)))

@gv_pc = (t (k (L o)))
  & L ~ ?((0 1) (t (k o)))

@gv_pc_leaf = (x (* x))

@gv_pc_node = (lm (t (k o)))
  & k ~ {k1 k2}
  & lm ~ {l1 l2}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 bt))
  & bt ~ ?((0 1) (t (k2 (l2 o))))
""")

    return b


if __name__ == "__main__":
    b = build_sp_count()
    path = os.path.join(D, "net.hvm")
    with open(path, "w") as f:
        f.write(b.text())
    print(f"Wrote {path}")
