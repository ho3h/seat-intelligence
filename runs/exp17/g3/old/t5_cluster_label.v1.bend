# t5_cluster_label: frontier min-label propagation over vertex-keyed tuple tries, then flatten.
#include base
#include cc
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walkp(es, zb(l), l, m)
  D = ccmin(A, n, l, m)
  return flat(D, l, 0, n, [])

def flat(t, l, base, n, acc):
  switch l:
    case 0:
      (d, f) = t
      if base < n:
        return List/Cons(d, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, n, flat(b, l-1, base + h, n, acc))
