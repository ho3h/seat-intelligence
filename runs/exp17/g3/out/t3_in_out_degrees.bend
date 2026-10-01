# t3_in_out_degrees: two count trees keyed by vertex id (tuple-trees, MSB first). Each edge applies one
# "increment leaf" update per tree; the updates' switches depend only on key and level, so the chain of m
# updates collapses level by level. The trees are flattened to lists in O(levels) depth.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (to, ti) = walk(es, zt(l), zt(l), l, m)
  return (flat(ti, l, 0, n, []), flat(to, l, 0, n, []))

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

def walk(es, to, ti, l, m):
  match es:
    case List/Nil:
      return (to, ti)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, inc(to, u, l, m), inc(ti, v, l, m), l, m)

# leaves with index < n, in order, consed onto acc
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
