# t5_cluster_merge_count: the number of merges that join two clusters is n minus the number of components of
# the accepted graph, whatever the processing order. Components by frontier min-label propagation over
# vertex-keyed tuple tries; count leaves whose label is their own id. A rejected triple becomes a harmless
# self loop, so the list walk has no data-dependent branch on its critical path.
#include base
#include ccb
def prog(x):
  (n, tau, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walkt(es, tau, zb(l), l, m)
  D = ccmin(A, n, l, m)
  return n - roots(D, l, 0, n)

def walkt(es, tau, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v, s) = es.head
      a = s >= tau
      v2 = u + a * (v - u)
      return walkt(es.tail, tau, pushb(pushb(A, u, l, m, v2), v2, l, m, u), l, m)

def roots(t, l, base, n):
  switch l:
    case 0:
      (d, f) = t
      return (d == base) & (base < n)
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return roots(a, l-1, base, n) + roots(b, l-1, base + h, n)
