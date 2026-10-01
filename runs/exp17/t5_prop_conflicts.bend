# t5_prop_conflicts: three walks in parallel, joined by return wires (unscoped lambdas).
# ---- exp17 shared library (plain Bend; tuple trees keyed by vertex id, MSB first) ----
# (Node first: a nullary Leaf with tag 0 would be merged with List/Nil by the compiler)
type Br:
  Node { e, l, r }
  Leaf

# (l, m): 2^l >= n, m = 2^(l-1) (0 when l = 0)
def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def mn(a, b):
  return a - (a > b) * (a - b)

def mx(a, b):
  return a + (b > a) * (b - a)

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def zinf(l):
  switch l:
    case 0:
      return 16777215
    case _:
      return (zinf(l-1), zinf(l-1))

def zl(l):
  switch l:
    case 0:
      return []
    case _:
      return (zl(l-1), zl(l-1))

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

def setk(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, setk(b, k, l-1, m >> 1, v))
      else:
        return (setk(a, k, l-1, m >> 1, v), b)

def addk(t, k, l, m, v):
  switch l:
    case 0:
      return t + v
    case _:
      (a, b) = t
      if k & m:
        return (a, addk(b, k, l-1, m >> 1, v))
      else:
        return (addk(a, k, l-1, m >> 1, v), b)

def ork(t, k, l, m, v):
  switch l:
    case 0:
      return t | v
    case _:
      (a, b) = t
      if k & m:
        return (a, ork(b, k, l-1, m >> 1, v))
      else:
        return (ork(a, k, l-1, m >> 1, v), b)

def mink(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, mink(b, k, l-1, m >> 1, x))
      else:
        return (mink(a, k, l-1, m >> 1, x), b)

def maxk(t, k, l, m, x):
  switch l:
    case 0:
      return t + (x > t) * (x - t)
    case _:
      (a, b) = t
      if k & m:
        return (a, maxk(b, k, l-1, m >> 1, x))
      else:
        return (maxk(a, k, l-1, m >> 1, x), b)

def getk(t, k, l, m):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      if k & m:
        return getk(b, k, l-1, m >> 1)
      else:
        return getk(a, k, l-1, m >> 1)

def sumt(t, l):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      return sumt(a, l-1) + sumt(b, l-1)

# first n leaves of a numeric tree as a list (tail threaded: the leaf conses are independent)
def flat(t, l, base, n, acc):
  switch l:
    case 0:
      if base < n:
        return List/Cons(t, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, n, flat(b, l-1, base + h, n, acc))

# list -> complete tree of 2^l leaves (in order; missing leaves = z); returns (tree, rest)
def fill(xs, l, z):
  switch l:
    case 0:
      match xs:
        case List/Nil:
          return (z, [])
        case List/Cons:
          return (xs.head, xs.tail)
    case _:
      (a, r1) = fill(xs, l-1, z)
      (b, r2) = fill(r1, l-1, z)
      return ((a, b), r2)

def popc(x):
  a = x - ((x >> 1) & 5592405)
  b = (a & 3355443) + ((a >> 2) & 3355443)
  c = (b + (b >> 4)) & 986895
  return ((c * 65793) >> 16) & 255

# multicast delivery: every leaf value v of B is applied to the sinks at the same leaf of Q
def deliver_all(B, Q, l):
  switch l:
    case 0:
      return deliver(B, Q)
    case _:
      (b1, b2) = B
      (q1, q2) = Q
      return deliver_all(b1, q1, l-1) + deliver_all(b2, q2, l-1)

def deliver(v, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(v) + deliver(v, sinks.tail)
# ---- end lib ----

# list -> (complete tree, levels): consumes the list once, doubling the tree (T, fill(next 2^k)) while cells remain
def grow0(xs):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      return grow(xs.tail, 0, xs.head)

def grow(xs, k, T):
  match xs:
    case List/Nil:
      return (T, k)
    case List/Cons:
      (T2, rest) = fill(xs, k, 0)
      return grow(rest, k + 1, (T, T2))

def topm(l):
  switch l:
    case 0:
      return 0
    case _:
      return 1 << (l-1)
# ---- end lib 2 ----

# list -> (tree, L, M): a length walk and a keyed-set walk run in parallel (the sets wait for L, then collapse)
def ltree(xs):
  (L, M) = lvl(ln(xs, 0), 0, 1)
  return (sw(xs, 0, zt(L), L, M), L, M)

def ln(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      return ln(xs.tail, a + 1)

def sw(xs, i, T, L, M):
  match xs:
    case List/Nil:
      return T
    case List/Cons:
      return sw(xs.tail, i + 1, setk(T, i, L, M, xs.head), L, M)

# attrs walk: keyed sets into A (tree keyed by node*4 + key; leaf (min, max) = (v, v), empty (INF, 0)).
# c walk: node i pushes a placeholder $a_i into bucket c[i] of G (keys are input data, so the pushes collapse
# early) and the sink "lambda $a_i" into leaf i of S. Delivery wires node i's 4-slot subtree of A into its
# placeholder; each cluster folds its members' slots leafwise with (min, max) and counts slots with min < max.
def prog(x):
  (c, at) = x
  (L, M) = lvl(ln(c, 0), 0, 1)
  (G, S) = cw(c, 0, zl(L), zl(L), L, M)
  A = aw(at, emp(L + 2), L + 2, M << 2)
  return cnt(G, L) + deliver_all(A, S, L)

def emp(l):
  switch l:
    case 0:
      return (16777215, 0)
    case _:
      return (emp(l-1), emp(l-1))

def cw(xs, i, G, S, L, M):
  match xs:
    case List/Nil:
      return (G, S)
    case List/Cons:
      return cw(xs.tail, i + 1, push(G, xs.head, L, M, $a), push(S, i, L, M, lambda $a: 0), L, M)

def aw(xs, A, L2, M2):
  match xs:
    case List/Nil:
      return A
    case List/Cons:
      (nd, k, v) = xs.head
      return aw(xs.tail, setk(A, (nd << 2) | k, L2, M2, (v, v)), L2, M2)

def cnt(G, l):
  switch l:
    case 0:
      return confl(fold4(G))
    case _:
      (a, b) = G
      return cnt(a, l-1) + cnt(b, l-1)

def fold4(xs):
  match xs:
    case List/Nil:
      return emp(2)
    case List/Cons:
      return comb(xs.head, fold4(xs.tail), 2)

def comb(a, b, l):
  switch l:
    case 0:
      (a1, a2) = a
      (b1, b2) = b
      return (mn(a1, b1), mx(a2, b2))
    case _:
      (x1, x2) = a
      (y1, y2) = b
      return (comb(x1, y1, l-1), comb(x2, y2, l-1))

def confl(s):
  ((s0, s1), (s2, s3)) = s
  return lt(s0) + lt(s1) + lt(s2) + lt(s3)

def lt(p):
  (a, b) = p
  return a < b
