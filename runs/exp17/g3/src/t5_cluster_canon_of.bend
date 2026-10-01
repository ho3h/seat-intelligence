# t5_cluster_canon_of: frontier reach from x over vertex-keyed tuple tries (keyed OR updates collapse level by
# level), then the largest reached id by a tree reduction.
#include base
#include cc
def prog(inp):
  (n, x, es) = inp
  (l, m) = lvl(n, 0, 1)
  A = walkp(es, zb(l), l, m)
  D = reach(A, x, l, m)
  return top(D, l, 0)

def top(t, l, base):
  switch l:
    case 0:
      (d, f) = t
      if d:
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
