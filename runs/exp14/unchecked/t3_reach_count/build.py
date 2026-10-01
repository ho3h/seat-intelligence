"""Build net.hvm for t3_reach_count: count vertices reachable from source s in a directed graph."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book, INF

def build():
    b = Book()

    # Core primitives
    G.lg(b)
    G.const_trie(b, "z0", "0")
    G.const_trie(b, "z1", "0")
    G.adjacency(b)
    G.update(b, "seed", "set1")

    # Reachability frontier with OR propagation
    reach_act = """(X (d (c (d2 (f m)))))
  & * ~ X
  & d ~ $([|] $(c d2_tmp))
  & d2_tmp ~ {d2 f}
  & 1 ~ m"""

    reach_msg = "(m (w r))\n  & * ~ w\n  & m ~ r"

    G.frontier(b, "reach", reach_act, reach_msg, "or", "0")

    # Count reachable vertices
    G.reduce(b, "cnt", "(x (1 o))\n  & x ~ $([+] $(1 o))", "+", idx=False, env=False)

    # Stream to walk edges
    G.stream(b, "w", 16,
        """((L g) ((u v) g2))
  & @gl_adj ~ (g (u (L ((v 0) g2))))""",
        "((* g) g)")

    # Main program
    b.add("""
@prog = ((n (s es)) out)
  & n ~ ?(((* 0) @p_pos) ((s es) out))
@p_pos = ((nm1 ((s es) out_in)) out)
  & @lg ~ (nm1 L)
  & L ~ {L_z0 {L_z1 {L_seed {L_w {L_f1 {L_f2 {L_cnt {* *}}}}}}}}
  & @z0 ~ (L_z0 D0)
  & @z1 ~ (L_z1 C0)
  & @seed ~ (C0 (s (L_seed (* C))))
  & D0 ~ {D0a D0b}
  & @w_blk ~ (es ((L_w D0a) G))
  & @reach_loop ~ ((G (D0b (C (L_f1 16777215)))) D)
  & @cnt ~ (D (L_cnt out_in))
  & * ~ L_f2
""")

    return b

if __name__ == "__main__":
    b = build()
    path = os.path.join(D, "net.hvm")
    open(path, "w").write(b.text())
    print("wrote", path)
