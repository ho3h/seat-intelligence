# t5_prop_majority: two independent walks in parallel: c -> membership bits M[i] = (c[i] == k) (keyed sets),
# attrs -> V[x] = (present, value) for the attrs with the wanted key (keyed sets; (node, key) is unique).
# A leafwise zip collects the cluster's values (tail-threaded, O(log n) deep); the mode (ties -> smallest)
# is taken over that short list by per-element counts and one max-reduce.
def prog(x):
  (k, key, c, attrs) = x
  n = len(c)
  (l, m) = lvl(n, 0, 1)
  M = mwalk(c, 0, zt(l), l, m, k)
  V = awalk(attrs, zp(l), l, m, key)
  vs = coll(M, V, l, [])
  (bc, bv) = best(vs, vs)
  return bv + (bc == 0) * (16777215 - bv)

def zp(l):
  switch l:
    case 0:
      return (0, 0)
    case _:
      return (zp(l-1), zp(l-1))

def mwalk(xs, i, M, l, m, k):
  match xs:
    case List/Nil:
      return M
    case List/Cons:
      return mwalk(xs.tail, i + 1, set(M, i, l, m, xs.head == k), l, m, k)

def setc(t, k, l, m, f, v):
  switch l:
    case 0:
      if f:
        return (1, v)
      else:
        return t
    case _:
      (a, b) = t
      if k & m:
        return (a, setc(b, k, l-1, m >> 1, f, v))
      else:
        return (setc(a, k, l-1, m >> 1, f, v), b)

def awalk(xs, V, l, m, key):
  match xs:
    case List/Nil:
      return V
    case List/Cons:
      (nd, ky, v) = xs.head
      return awalk(xs.tail, setc(V, nd, l, m, ky == key, v), l, m, key)

def coll(M, V, l, tl):
  switch l:
    case 0:
      (p, v) = V
      if M & p:
        return List/Cons(v, tl)
      else:
        return tl
    case _:
      (m1, m2) = M
      (v1, v2) = V
      return coll(m1, v1, l-1, coll(m2, v2, l-1, tl))

def count(xs, v):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return (xs.head == v) + count(xs.tail, v)

# (count, value) maximising count, then minimising value; (0, 0) for the empty list
def best(xs, all):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      v = xs.head
      c = count(all, v)
      (bc, bv) = best(xs.tail, all)
      t = (c > bc) | ((c == bc) & (v < bv))
      return (bc + t * (c - bc), bv + t * (v - bv))

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
