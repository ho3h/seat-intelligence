# t3_degrees: one count tree keyed by vertex id (tuple-tree, MSB first). Each edge applies two keyed
# increments; the updates' switches depend only on key and level, so the chain of 2m updates collapses
# level by level. The tree is flattened to the first n leaves in O(levels) depth (tail-threaded).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  return flat(walk(es, zt(l), l, m), l, 0, n, [])

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
