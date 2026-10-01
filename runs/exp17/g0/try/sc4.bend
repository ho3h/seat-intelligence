# t5_rewrite_sameas_cycle: pointer doubling with path minima and an early exit. Round j keeps, for every i,
# q(i) = p^(2^j)(i) and M(i) = min(p^1(i) .. p^(2^j)(i)) (the path strictly after i). One round is a gather
# of (q, M, root?) at q(i) for all i at once: the table is handed down the index tree (Bend duplicates it level
# by level) and each leaf does one keyed read. A non-root i with M(i) == i lies on a cycle (it came back to
# itself; a tree node never does), and once every q(i) is a root there is no cycle. Cycle nodes are caught as
# soon as 2^j reaches the cycle length; acyclic inputs stop after log2(longest chain) + 1 rounds. l + 1 rounds
# always suffice (2^l >= n), where the loop stops regardless.
def prog(p):
  n = len(p)
  (l, m) = lvl(n, 0, 1)
  P = cwalk(p, 0, zt(l), l, m)
  return loop(init(P, l, 0, n), l, m, l + 1)

def mn(a, b):
  return a + (b < a) * (b - a)

# leaf i: (q, M, root?) with q = p(i), M = p(i); padding leaves point to themselves as roots
def init(P, l, base, n):
  switch l:
    case 0:
      if base < n:
        return (P, P, P == base)
      else:
        return (base, base, 1)
    case _:
      (a, b) = P
      h = 1 << (l-1)
      return (init(a, l-1, base, n), init(b, l-1, base + h, n))

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

# one round: returns (new table, some cycle found, every target a root)
def rnd(T, S, lv, base, l, m):
  switch lv:
    case 0:
      (q, M, r) = S
      (q2, M2, r2) = get(T, q, l, m)
      M3 = mn(M, M2)
      return ((q2, M3, r), (M3 == base) & (r == 0), r2)
    case _:
      (s1, s2) = S
      h = 1 << (lv-1)
      (t1, c1, d1) = rnd(T, s1, lv-1, base, l, m)
      (t2, c2, d2) = rnd(T, s2, lv-1, base + h, l, m)
      return ((t1, t2), c1 | c2, d1 & d2)

def loop(T, l, m, k):
  (T2, cyc, done) = rnd(T, T, l, 0, l, m)
  if cyc:
    return 1
  else:
    if done:
      return 0
    else:
      switch k:
        case 0:
          return 0
        case _:
          return loop(T2, l, m, k-1)

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
