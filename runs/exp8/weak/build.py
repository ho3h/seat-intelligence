"""exp8 weak: 4 NEW graph programs from graphprims library."""
import sys, os, inspect
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(D))))
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

K = 16


def t3_bfs_dist():
    b = Book()
    G.lg(b)
    G.sssp(b, "sp")
    G.adjacency(b)
    G.stream(b, "w", K, """((L g) ((u v) (L2 g2)))
  & L ~ {L1 L2}
  & u ~ {u1 *}
  & v ~ {v1 *}
  & @gl_adj ~ (g (u1 (L1 ((v1 1) g2))))""", "((* g) g)")
    G.to_list(b, "tl")
    b.add("""
@prog = ((n (s es)) out)
  & n ~ {n0 {n1 n2}}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 *}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (s (L3 (16777215 (G D)))))
  & @tl ~ (D (L4 (0 (n2 ((0 *) out)))))
""")
    return b


def t3_khop():
    b = Book()
    G.lg(b)
    G.sssp(b, "sp")
    G.adjacency(b)
    G._sel(b)
    G.stream(b, "w", K, """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 1) g3))))""", "((* g) g)")
    G.reduce(b, "cnt", "(x (c o))\n  & x ~ $([<] $(16777215 f))\n  & f ~ ?(((* 0) 1) (c o))", "+")
    b.add("""
@prog = ((n (s (k es))) out)
  & n ~ {n0 {n1 *}}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 *}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (s (L3 (k (G D)))))
  & @cnt ~ (D (L4 (0 out)))
""")
    return b


def t3_cycle_rank():
    b = Book()
    G.lg(b)
    b.add("""
@prog = ((n es) out)
  & n ~ ?(((* *) @p_pos) (es out))
@p_pos = (* out)
""")
    return b


def t3_tree_parents():
    b = Book()
    G.lg(b)
    G.sssp(b, "sp")
    G.adjacency(b)
    G.stream(b, "w", K, """((L g) ((u v) (L3 g3)))
  & L ~ {L1 {L2 L3}}
  & u ~ {u1 u2}
  & v ~ {v1 v2}
  & @gl_adj ~ (g (u1 (L1 ((v1 1) g2))))
  & @gl_adj ~ (g2 (v2 (L2 ((u2 1) g3))))""", "((* g) g)")
    G.to_list(b, "tl")
    G.const_trie(b, "gl_inf", "16777215")
    b.add("""
@prog = ((n (r es)) out)
  & n ~ {n0 {n1 n2}}
  & n0 ~ $([-] $(1 nm1))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 {L3 {L4 {L5 *}}}}}
  & @gl_zl ~ (L1 G0)
  & @w_blk ~ (es ((L2 G0) G))
  & @sp_sssp ~ (n1 (r (L3 (16777215 (G D)))))
  & @tl ~ (D (L4 (0 (n2 ((0 *) out)))))
""")
    return b


def build_all():
    return {"t3_bfs_dist": t3_bfs_dist, "t3_khop": t3_khop, "t3_cycle_rank": t3_cycle_rank, "t3_tree_parents": t3_tree_parents}


if __name__ == "__main__":
    prog_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    all_progs = build_all()
    if prog_name == "all":
        for name, func in all_progs.items():
            book = func()
            path = os.path.join(D, f"{name}.hvm")
            with open(path, "w") as f:
                f.write(book.text())
            print(f"wrote {name}: {book.size()[0]} defs, {book.size()[1]} lines")
    else:
        if prog_name not in all_progs:
            print(f"unknown program: {prog_name}")
            sys.exit(1)
        book = all_progs[prog_name]()
        path = os.path.join(D, f"{prog_name}.hvm")
        with open(path, "w") as f:
            f.write(book.text())
        func_lines = len(inspect.getsource(all_progs[prog_name]).split('\n'))
        print(f"wrote {prog_name}: {book.size()[0]} defs, {book.size()[1]} lines (function {func_lines} lines)")
