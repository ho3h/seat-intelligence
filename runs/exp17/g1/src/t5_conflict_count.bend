# t5_conflict_count: the clustering list becomes a balanced tuple tree (a length walk and a keyed-set walk run in
# parallel); in parallel the must-not-link walk spawns, per pair, two keyed reads of that (future) tree and adds the
# comparison to an accumulator; the reads fire as soon as the tree exists.
def prog(x):
  (c, mnl) = x
  (C, L, M) = ltree(c)
  return walkm(mnl, C, L, M, 0)

def walkm(ps, C, L, M, acc):
  match ps:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = ps.head
      return walkm(ps.tail, C, L, M, acc + (getk(C, a, L, M) == getk(C, b, L, M)))
