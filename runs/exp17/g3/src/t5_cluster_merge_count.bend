# t5_cluster_merge_count: the number of merges that join two clusters is n minus the number of components of
# the accepted graph, whatever the processing order. Components by min labels in a stream dataflow (see ccs); count leaves whose label is their own id. A rejected triple becomes a harmless
# self loop, so the list walk has no data-dependent branch on its critical path.
#include base
#include ccs
def prog(x):
  (n, tau, es) = x
  (l, m) = lvl(n, 0, 1)
  (D, z) = ccs(acc(es, tau), l, m, 0, 16777215)
  return z + n - roots(D, l, 0, n)

# accepted pairs; a rejected triple becomes the self loop (u, u) (harmless for labels), so the list walk
# has no data-dependent branch
def acc(es, tau):
  match es:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, s) = es.head
      a = s >= tau
      return List/Cons((u, u + a * (v - u)), acc(es.tail, tau))

def roots(t, l, base, n):
  switch l:
    case 0:
      return (t == base) & (base < n)
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return roots(a, l-1, base, n) + roots(b, l-1, base + h, n)
