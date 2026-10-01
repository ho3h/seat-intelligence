# t5_cluster_members_of: frontier reach from x over vertex-keyed tuple tries, then the reached leaves in order.
#include base
#include cc
def prog(inp):
  (n, x, es) = inp
  (l, m) = lvl(n, 0, 1)
  A = walkp(es, zb(l), l, m)
  D = reach(A, x, l, m)
  return flat(D, l, 0, [])

def flat(t, l, base, acc):
  switch l:
    case 0:
      (d, f) = t
      if d:
        return List/Cons(base, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
