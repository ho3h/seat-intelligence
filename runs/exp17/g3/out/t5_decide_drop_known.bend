# t5_decide_drop_known: ids are unbounded (no n in the input), so no id-keyed trie; the known list is walked
# once into a Braun tree and each candidate tests membership with one balanced OR-reduction over it. The
# candidate walk's recursion does not wait for the test (the rest of the output is built first, the test
# only decides whether this cell is consed on).
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
  (ks, cs) = x
  (K, nk) = tobraun(ks, Br/Leaf, 0)
  return filt(cs, K)

def mem(t, u, v):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      (a, b) = t.e
      return ((a == u) & (b == v)) | mem(t.l, u, v) | mem(t.r, u, v)

def filt(cs, K):
  match cs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, s) = cs.head
      r = filt(cs.tail, K)
      if mem(K, u, v):
        return r
      else:
        return List/Cons((u, v, s), r)
