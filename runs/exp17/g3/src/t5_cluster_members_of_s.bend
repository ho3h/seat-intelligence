# t5_cluster_members_of: reach from x by a stream dataflow of max labels (see ccs), then the reached leaves in order.
#include base
#include ccs
def prog(inp):
  (n, x, es) = inp
  (l, m) = lvl(n, 0, 1)
  (D, z) = ccs(es, l, m, 1, x)
  return flat(D, l, 0, nilz(z))

def flat(t, l, base, acc):
  switch l:
    case 0:
      if t:
        return List/Cons(base, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
