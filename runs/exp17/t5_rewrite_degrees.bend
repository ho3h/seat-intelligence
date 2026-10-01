# t5_rewrite_degrees: as rewrite_collapsed (position-keyed c tree, edge walk in parallel with return-address
# sinks at u and v, every c value wired into its sinks), but each rewritten pair sets both bits (x, y) and
# (y, x) of a row bitset (tree keyed by (row, word), 16-bit words). The delivery pass also marks the fixed
# points c[i] == i (= the canonical ids); the output lists popcount(row x) for them, right to left.
def prog(x):
  (c, es) = x
  n = len(c)
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  L = l + lw
  C = cwalk(c, 0, zt(l), l, m)
  (Q, B) = ewalk(es, zl(l), zt(L), l, m, L, top(L), lw)
  (F, z) = dlv(C, Q, l, 0, n)
  return seq(z, outl(F, B, l, lw, []))

def ewalk(es, Q, B, l, m, L, M, lw):
  match es:
    case List/Nil:
      return (Q, B)
    case List/Cons:
      (u, v) = es.head
      Q2 = push(push(Q, u, l, m, lambda $cu: 0), v, l, m, lambda $cv: 0)
      (x, y) = minmax($cu, $cv)
      d = x != y
      B2 = setb(setb(B, (x << lw) | (y >> 4), L, M, d << (y & 15)), (y << lw) | (x >> 4), L, M, d << (x & 15))
      return ewalk(es.tail, Q2, B2, l, m, L, M, lw)

def minmax(a, b):
  t = b < a
  return (a + t * (b - a), b + t * (a - b))

def dlv(C, Q, l, base, n):
  switch l:
    case 0:
      return ((C == base) & (base < n), deliver(C, Q))
    case _:
      (c1, c2) = C
      (q1, q2) = Q
      h = 1 << (l-1)
      (f1, z1) = dlv(c1, q1, l-1, base, n)
      (f2, z2) = dlv(c2, q2, l-1, base + h, n)
      return ((f1, f2), z1 + z2)

def outl(F, B, l, lw, tl):
  switch l:
    case 0:
      if F:
        return List/Cons(pcount(B, lw), tl)
      else:
        return tl
    case _:
      (f1, f2) = F
      (b1, b2) = B
      return outl(f1, b1, l-1, lw, outl(f2, b2, l-1, lw, tl))

def seq(z, v):
  switch z:
    case 0:
      return v
    case _:
      return v

def len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len(xs.tail)

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

def zl(l):
  switch l:
    case 0:
      return []
    case _:
      return (zl(l-1), zl(l-1))

def set(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, set(b, k, l-1, m >> 1, v))
      else:
        return (set(a, k, l-1, m >> 1, v), b)

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

def push(t, k, l, m, v):
  switch l:
    case 0:
      return List/Cons(v, t)
    case _:
      (a, b) = t
      if k & m:
        return (a, push(b, k, l-1, m >> 1, v))
      else:
        return (push(a, k, l-1, m >> 1, v), b)

# c list -> tree keyed by position (keyed sets collapse level by level under the walk)
def cwalk(xs, i, C, l, m):
  match xs:
    case List/Nil:
      return C
    case List/Cons:
      return cwalk(xs.tail, i + 1, set(C, i, l, m, xs.head), l, m)

def deliver_all(C, Q, l):
  switch l:
    case 0:
      return deliver(C, Q)
    case _:
      (c1, c2) = C
      (q1, q2) = Q
      return deliver_all(c1, q1, l-1) + deliver_all(c2, q2, l-1)

def deliver(v, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(v) + deliver(v, sinks.tail)

def popc(x):
  a = x - ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b + (b >> 4)) & 3855
  return (c + (c >> 8)) & 31

def pcount(t, l):
  switch l:
    case 0:
      return popc(t)
    case _:
      (a, b) = t
      return pcount(a, l-1) + pcount(b, l-1)
