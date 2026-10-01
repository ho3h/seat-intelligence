# t5_cluster_sizes: canonical ids (component max) by a stream dataflow (see ccs); a block-threaded keyed
# histogram of the labels; then the counts at canonical leaves (label == id), in id order.
#include base
#include ccs
#include scatkv
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (D, z) = ccs(es, l, m, 1, 16777215)
  C = scatkv(kv(D, l, 0, n), l, l, m)
  return flat(D, C, l, 0, n, nilz(z))

def kv(D, l, base, n):
  switch l:
    case 0:
      return (D, base < n)
    case _:
      (a, b) = D
      h = 1 << (l-1)
      return (kv(a, l-1, base, n), kv(b, l-1, base + h, n))

def flat(t, c, l, base, n, acc):
  switch l:
    case 0:
      if (base < n) & (t == base):
        return List/Cons(c, acc)
      else:
        return acc
    case _:
      (a, b) = t
      (c1, c2) = c
      h = 1 << (l-1)
      return flat(a, c1, l-1, base, n, flat(b, c2, l-1, base + h, n, acc))
