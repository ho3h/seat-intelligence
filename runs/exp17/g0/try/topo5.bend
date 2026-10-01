# t3_topo_order: n fixed steps (no convergence test). Leaf v holds (remaining in-degree, in-neighbour bitset
# as a tree of 16-bit words); output vertices and padding are pushed to >= 2^20 so they never read as
# available. A step: leftmost available vertex a by a balanced reduce (two levels per call), then a is
# broadcast down and every leaf subtracts bit a of its own in-neighbour set (a local word read; no keyed
# routing, no row fetch). The frames of the next step exist before a is known, so only the number flows.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  L = l + lw
  (NB, G) = walk(es, zt(L), zt(l), l, m, lw, L, top(L))
  return steps(zip(pad(G, l, 0, n), NB, l), l, lw, mw, n)

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def top(L):
  switch L:
    case 0:
      return 0
    case _:
      return 1 << L-1

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def pad(G, l, base, n):
  switch l:
    case 0:
      return G + (base >= n) * 1048576
    case _:
      (a, b) = G
      h = 1 << (l-1)
      return (pad(a, l-1, base, n), pad(b, l-1, base + h, n))

def zip(G, NB, l):
  switch l:
    case 0:
      return (G, NB)
    case _:
      (a, b) = G
      (c, d) = NB
      return (zip(a, c, l-1), zip(b, d, l-1))

def add(t, k, l, m, v):
  switch l:
    case 0:
      return t + v
    case _:
      (a, b) = t
      if k & m:
        return (a, add(b, k, l-1, m >> 1, v))
      else:
        return (add(a, k, l-1, m >> 1, v), b)

def setb(t, k, l, m, bit):
  switch l:
    case 0:
      return t | bit
    case _:
      (a, b) = t
      if k & m:
        return (a, setb(b, k, l-1, m >> 1, bit))
      else:
        return (setb(a, k, l-1, m >> 1, bit), b)

def walk(es, NB, G, l, m, lw, L, M):
  match es:
    case List/Nil:
      return (NB, G)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, setb(NB, (v << lw) | (u >> 4), L, M, 1 << (u & 15)), add(G, v, l, m, 1), l, m, lw, L, M)

# (any available, index of the leftmost available); two levels per call
def am(S, l, base):
  switch l:
    case 0:
      (g, nb) = S
      return (g == 0, base)
    case 1:
      ((a, x), (b, y)) = S
      fa = a == 0
      fb = b == 0
      return (fa | fb, base + 1 - fa)
    case _:
      ((a, b), (c, d)) = S
      q = 1 << l
      h = q >> 1
      k = q >> 2
      (fa, ia) = am(a, l-2, base)
      (fb, ib) = am(b, l-2, base + k)
      (fc, ic) = am(c, l-2, base + h)
      (fd, id) = am(d, l-2, base + h + k)
      fab = fa | fb
      iab = ib + fa * (ia - ib)
      icd = id + fc * (ic - id)
      return (fab | fc | fd, icd + fab * (iab - icd))

# word a >> 4 of a word tree, returning the tree unchanged
def getw(t, k, lw, mw):
  switch lw:
    case 0:
      return (t, t)
    case _:
      (a, b) = t
      if k & mw:
        (b2, v) = getw(b, k, lw-1, mw >> 1)
        return ((a, b2), v)
      else:
        (a2, v) = getw(a, k, lw-1, mw >> 1)
        return ((a2, b), v)

def leaf(S, a, base, lw, mw):
  (g, nb) = S
  (nb2, w) = getw(nb, a >> 4, lw, mw)
  return (g - ((w >> (a & 15)) & 1) + (base == a) * 1048576, nb2)

def upd(S, a, l, base, lw, mw):
  switch l:
    case 0:
      return leaf(S, a, base, lw, mw)
    case 1:
      (x, y) = S
      return (leaf(x, a, base, lw, mw), leaf(y, a, base + 1, lw, mw))
    case _:
      ((s1, s2), (s3, s4)) = S
      q = 1 << l
      h = q >> 1
      k = q >> 2
      return ((upd(s1, a, l-2, base, lw, mw), upd(s2, a, l-2, base + k, lw, mw)), (upd(s3, a, l-2, base + h, lw, mw), upd(s4, a, l-2, base + h + k, lw, mw)))

def steps(S, l, lw, mw, k):
  switch k:
    case 0:
      return []
    case _:
      (f, a) = am(S, l, 0)
      return List/Cons(a, steps(upd(S, a, l, 0, lw, mw), l, lw, mw, k-1))
