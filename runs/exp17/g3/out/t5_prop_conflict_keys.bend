# t5_prop_conflict_keys: c is walked once into a Braun tree (index access O(log n), n counted on the way);
# every attribute reads c[x] and applies an order-independent "merge value" update at key (c[x], key) of a
# tuple trie (leaf: (seen, first value, conflict)); keyed updates collapse level by level along the walk.
# The conflicting leaves, in key order, are the sorted output.
# ---- base: tuple tries keyed by vertex id (MSB first), l levels, m = top-bit mask
type Br:
  Node { e, l, r }
  Leaf

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l, z):
  switch l:
    case 0:
      return z
    case _:
      return (zt(l-1, z), zt(l-1, z))

def zb(l):
  switch l:
    case 0:
      return Br/Leaf
    case _:
      return (zb(l-1), zb(l-1))

def bins(t, e):
  match t:
    case Br/Leaf:
      return Br/Node(e, Br/Leaf, Br/Leaf)
    case Br/Node:
      return Br/Node(e, bins(t.r, t.e), t.l)

def pushb(t, k, l, m, e):
  switch l:
    case 0:
      return bins(t, e)
    case _:
      (a, b) = t
      if k & m:
        return (a, pushb(b, k, l-1, m >> 1, e))
      else:
        return (pushb(a, k, l-1, m >> 1, e), b)

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

def get(t, k, l, m):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      if k & m:
        return get(b, k, l-1, m >> 1)
      else:
        return get(a, k, l-1, m >> 1)

def updmin(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmin(b, k, l-1, m >> 1, x))
      else:
        return (updmin(a, k, l-1, m >> 1, x), b)

def updmax(t, k, l, m, x):
  switch l:
    case 0:
      return t + (x > t) * (x - t)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmax(b, k, l-1, m >> 1, x))
      else:
        return (updmax(a, k, l-1, m >> 1, x), b)
# ---- braun: a list walked once into a Braun tree by cons at the root (the chain of conses is pipelined:
# each cons rebuilds the root immediately). Index 0 = the LAST list element; bget(t, i) is O(log n).
def tobraun(xs, t, c):
  match xs:
    case List/Nil:
      return (t, c)
    case List/Cons:
      return tobraun(xs.tail, bins(t, xs.head), c + 1)

def bget(t, i):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      if i == 0:
        return t.e
      else:
        if i & 1:
          return bget(t.l, (i - 1) >> 1)
        else:
          return bget(t.r, (i - 2) >> 1)
def prog(x):
  (cs, attrs) = x
  (C, n) = tobraun(cs, Br/Leaf, 0)
  (l, m) = lvl(n << 2, 0, 1)
  B = walk(attrs, C, n - 1, zt(l, (0, 0, 0)), l, m)
  return flat(B, l, 0, [])

def mv(t, k, l, m, v):
  switch l:
    case 0:
      (h, v0, cf) = t
      return (1, v0 * h + v * (1 - h), cf | (h & (v != v0)))
    case _:
      (a, b) = t
      if k & m:
        return (a, mv(b, k, l-1, m >> 1, v))
      else:
        return (mv(a, k, l-1, m >> 1, v), b)

def walk(es, C, n1, B, l, m):
  match es:
    case List/Nil:
      return B
    case List/Cons:
      (u, k, v) = es.head
      cu = bget(C, n1 - u)
      return walk(es.tail, C, n1, mv(B, (cu << 2) | k, l, m, v), l, m)

def flat(t, l, base, acc):
  switch l:
    case 0:
      (h, v0, cf) = t
      if cf:
        return List/Cons((base >> 2, base & 3), acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
