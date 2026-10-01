# t3_topo_order: n fixed steps (no convergence test). Leaf v holds (remaining in-degree, in-neighbour bitset
# as a tree of 16-bit words); output vertices and padding are pushed to >= 2^20 so they never read as
# available. A step: leftmost available vertex a by a balanced reduce (two levels per call), then a is
# broadcast down and every leaf subtracts bit a of its own in-neighbour set (a local word read, selected
# arithmetically so no switch waits on a; output and available leaves skip it; no keyed
# routing, no row fetch). The frames of the next step exist before a is known, so only the number flows.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  L = l + lw
  (NB, G) = walk(es, zt(L), zt(l), l, m, lw, L, top(L))
  S = zip(pad(G, l, 0, n), NB, l)
  (f, a) = am(S, l, 0)
  return steps(S, a, l, lw, mw, n)

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

# word k of a word tree, selected arithmetically (no switch waits on k), returning the tree unchanged
def selw(t, k, lw):
  switch lw:
    case 0:
      return (t, t)
    case _:
      (a, b) = t
      (a2, x) = selw(a, k, lw-1)
      (b2, y) = selw(b, k, lw-1)
      c = (k >> (lw-1)) & 1
      return ((a2, b2), x + c * (y - x))

# bit a of the leaf's in-neighbour set = OR over words of (word & M), M = one-hot mask of a (built once
# per step at the root and broadcast); output and available leaves (nothing to subtract) skip it
def hit(t, M, lw):
  switch lw:
    case 0:
      return (t, t & M)
    case _:
      (a, b) = t
      (m1, m2) = M
      (a2, x) = hit(a, m1, lw-1)
      (b2, y) = hit(b, m2, lw-1)
      return ((a2, b2), x | y)

def leaf(S, a, M, base, lw, mw):
  (g, nb) = S
  if (g == 0) | (g >= 1048576):
    return (g + (base == a) * 1048576, nb)
  else:
    (nb2, w) = hit(nb, M, lw)
    return (g - (w != 0), nb2)

def unit(lw, wbase, v):
  switch lw:
    case 0:
      return (wbase == (v >> 4)) << (v & 15)
    case _:
      h = 1 << (lw-1)
      return (unit(lw-1, wbase, v), unit(lw-1, wbase + h, v))

def leaf2(S, a, M, base, lw, mw):
  (g2, nb2) = leaf(S, a, M, base, lw, mw)
  return ((g2, nb2), g2 == 0, base)

def sel(fa, ia, fb, ib):
  return (fa | fb, ib + fa * (ia - ib))

# one traversal: apply step a and reduce the next argmin (leftmost available) on the way up
def upd(S, a, M, l, base, lw, mw):
  switch l:
    case 0:
      return leaf2(S, a, M, base, lw, mw)
    case 1:
      (x, y) = S
      (x2, fa, ia) = leaf2(x, a, M, base, lw, mw)
      (y2, fb, ib) = leaf2(y, a, M, base + 1, lw, mw)
      return ((x2, y2), fa | fb, ib + fa * (ia - ib))
    case _:
      ((s1, s2), (s3, s4)) = S
      q = 1 << l
      h = q >> 1
      k = q >> 2
      (t1, fa, ia) = upd(s1, a, M, l-2, base, lw, mw)
      (t2, fb, ib) = upd(s2, a, M, l-2, base + k, lw, mw)
      (t3, fc, ic) = upd(s3, a, M, l-2, base + h, lw, mw)
      (t4, fd, id) = upd(s4, a, M, l-2, base + h + k, lw, mw)
      fab = fa | fb
      iab = ib + fa * (ia - ib)
      icd = id + fc * (ic - id)
      return (((t1, t2), (t3, t4)), fab | fc | fd, icd + fab * (iab - icd))

def steps(S, a, l, lw, mw, k):
  switch k:
    case 0:
      return []
    case _:
      (S2, f, a2) = upd(S, a, unit(lw, 0, a), l, 0, lw, mw)
      return List/Cons(a, steps(S2, a2, l, lw, mw, k-1))
