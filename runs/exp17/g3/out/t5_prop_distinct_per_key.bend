# t5_prop_distinct_per_key: values below 256 go into a presence bitset keyed by (key, value) (64 words of 16
# bits, keyed OR updates during the list walk, collapsing level by level; branch-free: other values OR 0);
# per key a popcount reduction. Values >= 256 (allowed by the spec, rare in practice) are handled exactly by
# a Braun tree of only those elements, with unique heap ids: each checks in one balanced reduction whether
# a smaller-id element has the same (key, value).
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
def prog(x):
  (T, W) = walk(x, Br/Leaf, zt(6, 0))
  L = lab(T, 1)
  (a, b, c, d) = outer(L, L)
  (w0, w1) = W
  (x0, x1) = w0
  (x2, x3) = w1
  return [a + pops(x0, 4), b + pops(x1, 4), c + pops(x2, 4), d + pops(x3, 4)]

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

def walk(xs, T, W):
  match xs:
    case List/Nil:
      return (T, W)
    case List/Cons:
      (u, k, v) = xs.head
      sm = v < 256
      W2 = orb(W, (k << 4) | ((v >> 4) & 15), 6, 32, sm << (v & 15))
      return walk(xs.tail, bigs(T, k, v), W2)

def bigs(T, k, v):
  if v < 256:
    return T
  else:
    return bins(T, (k, v))

def pop16(x):
  a = (x & 21845) + ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b & 3855) + ((b >> 4) & 3855)
  return (c & 255) + (c >> 8)

def pops(t, l):
  switch l:
    case 0:
      return pop16(t)
    case _:
      (a, b) = t
      return pops(a, l-1) + pops(b, l-1)

def lab(t, i):
  match t:
    case Br/Leaf:
      return Br/Leaf
    case Br/Node:
      (k, v) = t.e
      return Br/Node((k, v, i), lab(t.l, i << 1), lab(t.r, (i << 1) | 1))

def inner(t, k, v, i):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      (k2, v2, i2) = t.e
      return ((k2 == k) & (v2 == v) & (i2 < i)) | inner(t.l, k, v, i) | inner(t.r, k, v, i)

def outer(t, Z):
  match t:
    case Br/Leaf:
      return (0, 0, 0, 0)
    case Br/Node:
      (k, v, i) = t.e
      (a1, b1, c1, d1) = outer(t.l, Z)
      (a2, b2, c2, d2) = outer(t.r, Z)
      f = 1 - inner(Z, k, v, i)
      return (a1 + a2 + f * (k == 0), b1 + b2 + f * (k == 1), c1 + c2 + f * (k == 2), d1 + d2 + f * (k == 3))
