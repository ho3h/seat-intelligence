# t3_sources_sinks: two bitmaps as complete tuple-trees keyed by vertex id (MSB first).
# Each edge applies one "set leaf" update per tree; an update's switches depend only on the key and
# the level, so a chain of updates collapses level by level without waiting for the tree data.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (to, ti) = walk(es, zt(l), zt(l), l, m)
  return (n - cnt(ti, l), n - cnt(to, l))

# smallest l with 2^l >= n, and the top mask 2^(l-1) (0 when l == 0)
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

def set(t, k, l, m):
  switch l:
    case 0:
      return 1
    case _:
      (a, b) = t
      if k & m:
        return (a, set(b, k, l-1, m >> 1))
      else:
        return (set(a, k, l-1, m >> 1), b)

def walk(es, to, ti, l, m):
  match es:
    case List/Nil:
      return (to, ti)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, set(to, u, l, m), set(ti, v, l, m), l, m)

def cnt(t, l):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      return cnt(a, l-1) + cnt(b, l-1)
