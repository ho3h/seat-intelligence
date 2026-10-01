"""Build HVM2 net for t5_rewrite_sameas_roots - final attempt."""
import sys, os

script_dir = os.path.dirname(os.path.abspath(__file__))
genome_root = os.path.join(script_dir, "..", "..", "..", "..")
sys.path.insert(0, genome_root)

from genome.lib.graphprims import Book

def build():
    book = Book()

    # Simple sequential algorithm:
    # Walk through input list and resolve each pointer to its root

    book.add("""
@prog = (lst out)
  & @walk ~ (lst out)

// Walk through the list and resolve pointers
@walk = (lst out)
  & lst ~ (?((@done @step) out) *)

// Empty list: return empty list
@done = (* out)
  & out ~ (0 *)

// Process one element: resolve its pointer and continue
@step = ((h t) out)
  & @resolve ~ (h t (r r_list))
  & out ~ (1 (r r_list))

// Resolve pointer h in context of list t
// Keep the list t for future lookups
@resolve = (h t (r r_list))
  & @check_pointer ~ (h h (t (r r_list)))

// Check if h points to itself (is root) or points elsewhere
@check_pointer = (h h_copy (t (r r_list)))
  & h ~ (h_val cmp_result)
  & h_val ~ ?((@is_root @not_root) (h_copy (t (r r_list))))
  & cmp_result ~ *

// h is a root: return h and continue the list walk
@is_root = (* (h_copy (t (r r_list))))
  & r ~ h_copy
  & @walk ~ (t r_list)

// h is not a root: follow the pointer
@not_root = ((h_next *) (h_copy (t (r r_list))))
  & @resolve ~ (h_next t (r r_list))
  & h_copy ~ *
""")

    path = os.path.join(os.path.dirname(__file__), "net.hvm")
    with open(path, 'w') as f:
        f.write(book.text())
    print(f"Wrote {path}")

if __name__ == "__main__":
    build()
