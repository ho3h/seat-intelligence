"""Build t5_conflict_flags HVM2 net using graphprims library."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
# Add Genome root to path (go up: unchecked/t5_conflict_flags -> unchecked -> exp14 -> runs -> Genome)
sys.path.insert(0, os.path.join(D, "..", "..", "..", ".."))
from genome.lib import graphprims as G
from genome.lib.graphprims import Book

def t5_conflict_flags():
    # Input: (c, mnl) where:
    #   c is a list of cluster canonical ids (length n)
    #   mnl is a list of must-not-link pairs (a, b)
    # Output: list of conflict flags
    #
    # Algorithm:
    # 1. Build a trie C from c: C[i] = c[i]
    # 2. For each mnl pair (a, b), if c[a] == c[b], mark cluster c[a]
    # 3. Output conflict flags

    b = Book()
    G.lg(b)
    G.const_trie(b, "z0", "0")
    G.update(b, "c_upd", "set")
    G.update(b, "conf_or", "or")
    G.get(b, "get_c")
    G.to_list(b, "tl")

    b.add("""
@prog = ((c mnl) out)
  & @z0 ~ (24 ct)
  & @z0 ~ (24 conf)
  & @c_fill ~ (c (0 (ct (mnl (24 (conf out))))))

// Build clustering trie from list c
@c_fill = (c_list (idx (ct (mnl (L (conf out))))))
  & c_list ~ ?((@c_end @c_next) (idx (ct (mnl (L (conf out))))))

@c_end = (* (idx (ct (mnl (L (conf out))))))
  & idx ~ *
  & @mnl_proc ~ (mnl (L (ct (conf out))))

@c_next = (* ((val rest) (idx (ct (mnl (L (conf out)))))))
  & L ~ {L1 {L2 L3}}
  & idx ~ {i1 {i2 i3}}
  & @c_upd ~ (ct (i1 (L1 (val ct2))))
  & i4 ~ $([+1] i2)
  & @c_fill ~ (rest (i4 (ct2 (mnl (L2 (L3 (conf out)))))))

// Process must-not-link pairs
@mnl_proc = (mnl (L (ct (conf out))))
  & L ~ {L1 {L2 L3}}
  & ct ~ {ct1 ct2}
  & mnl ~ ?((@mnl_end @mnl_next) (L1 (ct1 (conf out))))
  & @mnl_stub ~ (L2 (L3 (ct2 (mnl))))

@mnl_stub = (L2 (L3 (ct2 (mnl))))
  & mnl ~ *(L2 (L3 (ct2 (*))))

@mnl_end = (* (L1 (ct1 (conf out))))
  & @tl ~ (conf (L1 (0 (out))))

@mnl_next = (* (((a b) rest) (L1 (ct1 (conf out)))))
  & a ~ {a1 {a2 a3}}
  & ct2 ~ {ct2a ct2b}
  & L2 ~ {L2a L2b}
  & L3 ~ {L3a L3b}
  & @get_c ~ (ct1 (a1 (L2a (ca))))
  & @get_c ~ (ct2a (b (L2b (cb))))
  & ca ~ ?((@conflict @no_conflict) (cb (a3 (rest (L3 (conf out))))))

@conflict = (cb (a3 (rest (L3 (conf out)))))
  & L3 ~ {L3a L3b}
  & @conf_or ~ (conf (ca (L3a (1 (conf2)))))
  & @mnl_proc ~ (rest (L3b (ct2b (conf2 out))))

@no_conflict = (* (cb (a3 (rest (L3 (conf out))))))
  & L3 ~ {L3a L3b}
  & @mnl_proc ~ (rest (L3b (ct2b (conf out))))
""")

    return b

if __name__ == "__main__":
    b = t5_conflict_flags()
    out_path = os.path.join(D, "net.hvm")
    open(out_path, "w").write(b.text())
    print(f"wrote {out_path}")
