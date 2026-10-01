# t5_cluster_canon_of: reach from x by a stream dataflow of max labels (see ccs) , then the largest reached id by a tree reduction.
#include base
#include ccs
def prog(inp):
  (n, x, es) = inp
  (l, m) = lvl(n, 0, 1)
  (D, z) = ccs(es, l, m, 1, x)
  return z + top(D, l, 0)

def top(t, l, base):
  switch l:
    case 0:
      if t:
        return base
      else:
        return 0
    case _:
      (a, b) = t
      h = 1 << (l-1)
      tb = top(b, l-1, base + h)
      ta = top(a, l-1, base)
      return mx(ta, tb)

def mx(a, b):
  return a + (b > a) * (b - a)
