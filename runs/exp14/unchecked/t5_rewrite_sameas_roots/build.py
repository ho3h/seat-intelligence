#!/usr/bin/env python3
"""
Build script for t5_rewrite_sameas_roots: SAME_AS pointer resolution.

Simple direct implementation in HVM without advanced library features.
"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(D)))))
from genome.lib import graphprims as G
from genome.lib.graphprims import Book, INF

def build():
    b = Book()

    # Simple program that processes the list
    b.add("""
@prog = ((n ptrs_list) out)
  & n ~ ?(((* (0 *)) @handle_empty) (handle_nonempty (ptrs_list out)))

@handle_empty = (o o)

@handle_nonempty = ((n ptrs_list) out)
  & @process_list ~ (ptrs_list (ptrs_list ((0 *) out)))

// Process each element of the input list
// State: (original_list (position (result_acc out)))
@process_list = (list (list_orig (result_acc (out))))
  & list ~ (?(nil cons) out)

@nil = (l (r r))

@cons = ((h t) (out))
  & h ~ ptr_val
  & t ~ rest
  & @find_root ~ (ptr_val (list_orig (h (result_acc (out2)))))
  & @process_list ~ (rest (list_orig ((1 (h out2)) out3)))

// Find root for a given pointer value
// Trace: (current_index original_list (output element_to_emit result_acc out))
@find_root = (idx (list (out (result (out_final)))))
  & idx ~ $([=] $(idx eq_check))
  & eq_check ~ ?((@at_root @not_root) (list (idx (out (result (out_final))))))

@at_root = (list (* (idx (out))))
  & idx ~ out

@not_root = (list (idx (out (result (out_final)))))
  & @get_at ~ (list (idx (next_idx (out (result (out_final))))))
  & @find_root ~ (next_idx (list (out (result (out_final)))))

// Get element at position idx in list
@get_at = (list (idx (result (out (result_acc (out_final))))))
  & idx ~ $([=] $(0 is_zero))
  & is_zero ~ ?((@get_at_0 @get_at_rest) (list (idx (result (out (result_acc (out_final)))))))

@get_at_0 = (list (* (result (result (result_acc (out_final))))))
  & list ~ (?(nil cons) out)
  & nil ~ (* (* * *))
  & cons ~ ((h t) (out2))
  & result ~ h

@get_at_rest = (list (idx (result (out (result_acc (out_final))))))
  & idx ~ $([-] $(1 idx2))
  & list ~ (?(nil cons) out)
  & nil ~ (* (* * *))
  & cons ~ ((h t) (out2))
  & @get_at ~ (t (idx2 (result (out (result_acc (out_final))))))
""")

    return b

if __name__ == "__main__":
    path = os.path.join(D, "net.hvm")
    open(path, "w").write(build().text())
    print("wrote", path)
