"""Build t5_conflict_count net.

Input: (c, mnl)
  c = clustering list
  mnl = must-not-link pairs list
Output: count of violated pairs (c[a] == c[b])
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(D), '..', '..', '..'))
from genome.lib import graphprims as Book

def build():
    b = Book.Book()

    b.add("""
@prog = ((c mnl) out)
  & @walk_pairs ~ (c (mnl (0 out)))

// Walk pairs in mnl, count violations
@walk_pairs = (c (mnl (cnt out)))
  & mnl ~ ?(((@pair_nil @pair_cons) c) (cnt out))

@pair_nil = (c (cnt out))
  & c ~ *
  & cnt ~ out

@pair_cons = (* (((a (b *)) rest) (c (cnt out))))
  & c ~ {c1 {c2 c3}}
  & @get_c ~ (c1 (a (ca *)))
  & @get_c ~ (c2 (b (cb *)))
  & ca ~ $([=] $(cb eq))
  & eq ~ ?((@vio_no @vio_yes) (rest (c3 (cnt out))))

@vio_no = (rest (c (cnt out)))
  & @walk_pairs ~ (c (rest (cnt out)))

@vio_yes = (* (rest (c (cnt out))))
  & cnt ~ $([+1] cnt2)
  & @walk_pairs ~ (c (rest (cnt2 out)))

// Get value at index from list
// Usage: @get_c ~ (list (idx (val *)))
@get_c = (lst (idx (val res)))
  & idx ~ ?((@gc_zero @gc_succ) val)

@gc_zero = (val (val *))

@gc_succ = (* (idx_pred (lst_tail (val res))))
  & lst ~ ?(((@gc_empty @gc_item) idx_pred) res)

@gc_empty = (idx (val res))
  & idx ~ *
  & val ~ 0

@gc_item = (* (((v t) idx_pred) (val res)))
  & v ~ *
  & @get_c ~ (t (idx_pred (val res)))
""")

    return b

if __name__ == "__main__":
    b = build()
    output_path = os.path.join(D, "net.hvm")
    with open(output_path, "w") as f:
        f.write(b.text())
    sizes = b.size()
    print(f"wrote {output_path}")
    print(f"{sizes[0]} defs, {sizes[1]} lines")
