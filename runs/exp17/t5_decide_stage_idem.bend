# t5_decide_stage_idem: keyed trees + return wires + an order-preserving filter whose cells are independent.
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

# key = target * 8 + verb. The ledger walk ORs a block flag (status <= 1) into Bl; the proposal walk (in parallel)
# min-updates the index of each key's first proposal into F (keys are input data, so both collapse once the depth
# is known), plants a sink for (block, first) at the key, and builds the output as a chain of pick(keep_i, p_i,
# rest) cells, each waiting only for its own keep_i = !block & first == i.
def prog(x):
  (ld, ps) = x
  (Lt, Mt) = lvl(mx(mxl(ld, 0), mxp(ps, 0)) + 1, 0, 1)
  L = Lt + 3
  M = Mt << 3 | (4 * (Lt == 0))
  Bl = lw(ld, zt(L), L, M)
  (out, F, Q) = pw(ps, 0, zinf(L), zl(L), L, M)
  z = deliver_all(zip(Bl, F, L), Q, L)
  if z == 0:
    return out
  else:
    return out

def mxl(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      (vb, t, st) = xs.head
      return mxl(xs.tail, mx(a, t))

def mxp(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      (vb, t) = xs.head
      return mxp(xs.tail, mx(a, t))

def lw(xs, B, L, M):
  match xs:
    case List/Nil:
      return B
    case List/Cons:
      (vb, t, st) = xs.head
      return lw(xs.tail, ork(B, t * 8 + vb, L, M, st <= 1), L, M)

def pw(xs, i, F, Q, L, M):
  match xs:
    case List/Nil:
      return ([], F, Q)
    case List/Cons:
      (vb, t) = xs.head
      k = t * 8 + vb
      (rest, F2, Q2) = pw(xs.tail, i + 1, mink(F, k, L, M, i), push(Q, k, L, M, lambda $bf: 0), L, M)
      (b, f) = $bf
      return (pick((b == 0) & (f == i), (vb, t), rest), F2, Q2)

def pick(k, p, r):
  if k:
    return List/Cons(p, r)
  else:
    return r

def zip(a, b, l):
  switch l:
    case 0:
      return (a, b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (zip(a1, b1, l-1), zip(a2, b2, l-1))
