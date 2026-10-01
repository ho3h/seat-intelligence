# t5_rewrite_neighbours: c is walked once into a Braun tree (index access in O(log n), n counted on the way);
# every edge reads c[u], c[v] and ORs a flag at key "the other end" into a vertex-keyed tuple trie when exactly
# one end maps to k (branch-free: a non-matching edge ORs 0). The trie's flagged leaves, in order.
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
  (k, cs, es) = x
  (C, n) = tobraun(cs, Br/Leaf, 0)
  (l, m) = lvl(n, 0, 1)
  F = walk(es, C, n - 1, k, zt(l, 0), l, m)
  return flat(F, l, 0, [])

def orb(t, k, l, m, b):
  switch l:
    case 0:
      return t | b
    case _:
      (a, c) = t
      if k & m:
        return (a, orb(c, k, l-1, m >> 1, b))
      else:
        return (orb(a, k, l-1, m >> 1, b), c)

def walk(es, C, n1, k, F, l, m):
  match es:
    case List/Nil:
      return F
    case List/Cons:
      (u, v) = es.head
      cu = bget(C, n1 - u)
      cv = bget(C, n1 - v)
      f = (cu == k) ^ (cv == k)
      return walk(es.tail, C, n1, k, orb(F, cu + cv - k, l, m, f), l, m)

def flat(t, l, base, acc):
  switch l:
    case 0:
      if t:
        return List/Cons(base, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
