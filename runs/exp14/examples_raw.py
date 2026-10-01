"""Worked examples for the UNCHECKED API (genome/lib/graphprims.py + raw HVM glue): t3_degrees and t3_cc_largest,
exactly as the strong author wrote them (runs/exp8/build.py).
usage: python3 runs/exp14/examples_raw.py  -> runs/exp14/raw_t3_degrees.hvm, runs/exp14/raw_t3_cc_largest.hvm"""
import sys, os
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


def t3_degrees():
    # Input (n, edges), undirected. Output: list of n degrees.
    # walker state (L h); element (u v); dinc = update with act inc (payload ignored: pass *); fin erases L.
    # @prog: n == 0 -> (0 *) (the empty list); else L = lg(n-1), H0 = zeros, walk, to_list of the first n leaves.
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


def t3_cc_largest():
    # Input (n, edges), undirected. Output: size of the largest connected component (0 for n = 0).
    # min-label relax (cc_loop) -> scatter histogram (add 1 at key label[i], only for i < n) -> reduce max.
    # L is needed 9 times, hence the DUP chain {L1 {L2 ...}}; cc_loop's budget X = 16777215 means "no budget".
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


if __name__ == "__main__":
    for f in (t3_degrees, t3_cc_largest):
        path = os.path.join(D, "raw_" + f.__name__ + ".hvm")
        open(path, "w").write(f().text())
        print("wrote", path)
