# t5_cluster_singletons: n minus the number of distinct endpoints. One walk sets flags with keyed updates in a
# vertex-keyed tuple tree (the updates' switches depend only on the input keys, so the chain collapses level by
# level), then a balanced count of unflagged real leaves.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  return cz(walk(es, zt(l), l, m), l, 0, n)

def walk(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, setk(setk(T, u, l, m, 1), v, l, m, 1), l, m)

def cz(t, l, base, n):
  switch l:
    case 0:
      return (t == 0) & (base < n)
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return cz(a, l-1, base, n) + cz(b, l-1, base + h, n)
