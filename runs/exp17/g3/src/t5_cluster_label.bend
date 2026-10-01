# t5_cluster_label: component min labels by a stream dataflow (see ccs), then flatten.
#include base
#include ccs
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (D, z) = ccs(es, l, m, 0, 16777215)
  return flat(D, l, 0, n, nilz(z))

def flat(t, l, base, n, acc):
  switch l:
    case 0:
      if base < n:
        return List/Cons(t, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, n, flat(b, l-1, base + h, n, acc))
