# t3_line_graph_edges: one degree tree keyed by vertex id; each edge increments two leaves (keyed updates
# that collapse level by level); then a balanced reduction of d*(d-1)/2 over the leaves.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  return pairs(walk(es, zt(l), l, m), l)

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def inc(t, k, l, m):
  switch l:
    case 0:
      return t + 1
    case _:
      (a, b) = t
      if k & m:
        return (a, inc(b, k, l-1, m >> 1))
      else:
        return (inc(a, k, l-1, m >> 1), b)

def walk(es, t, l, m):
  match es:
    case List/Nil:
      return t
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, inc(inc(t, u, l, m), v, l, m), l, m)

def pairs(t, l):
  switch l:
    case 0:
      return (t * (t - 1)) / 2
    case _:
      (a, b) = t
      return pairs(a, l-1) + pairs(b, l-1)
