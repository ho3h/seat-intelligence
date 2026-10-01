# t5_decide_drop_known: ids are unbounded (no n in the input), so no id-keyed trie; the known list is walked
# once into a Braun tree and each candidate tests membership with one balanced OR-reduction over it. The
# candidate walk's recursion does not wait for the test (the rest of the output is built first, the test
# only decides whether this cell is consed on).
#include base
#include braun
def prog(x):
  (ks, cs) = x
  (K, nk) = tobraun(ks, Br/Leaf, 0)
  return filt(cs, K)

def mem(t, u, v):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      (a, b) = t.e
      return ((a == u) & (b == v)) | mem(t.l, u, v) | mem(t.r, u, v)

def filt(cs, K):
  match cs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, s) = cs.head
      r = filt(cs.tail, K)
      if mem(K, u, v):
        return r
      else:
        return List/Cons((u, v, s), r)
