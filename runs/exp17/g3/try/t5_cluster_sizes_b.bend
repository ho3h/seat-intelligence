# t5_cluster_sizes: canonical ids by frontier max-label propagation over vertex-keyed tuple tries; a
# block-threaded keyed histogram of the labels; then the counts at canonical leaves (label == id), in id order.
#include base
#include ccb
#include scat
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walkp(es, zb(l), l, m)
  D = ccmax(A, n, l, m)
  C = scat(D, l, 0, n, l, m)
  return flat(D, C, l, 0, n, [])

def flat(t, c, l, base, n, acc):
  switch l:
    case 0:
      (d, f) = t
      if (base < n) & (d == base):
        return List/Cons(c, acc)
      else:
        return acc
    case _:
      (a, b) = t
      (c1, c2) = c
      h = 1 << (l-1)
      return flat(a, c1, l-1, base, n, flat(b, c2, l-1, base + h, n, acc))
