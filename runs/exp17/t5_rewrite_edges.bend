# t5_rewrite_edges: bitsets + return wires, no data-dependent keyed routing.
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

# c walks: C = the clustering as a tuple tree (ltree), and node u pushes a placeholder $t_u into bucket c[u] of K
# (keys are input data, so these pushes collapse early), with the sink for $t_u at leaf u of P.
# edge walk (parallel): bucket u of E gets a placeholder $y for c[v] and bucket v one for c[u]; their sinks go to Q.
# After delivering C into Q: T_u = OR over E_u of onehot(c[v]) (a word-tree bitset over cluster ids); after
# delivering T into P: R_x = OR over K_x of T_u, the set of clusters adjacent to cluster x. Output: tail-threaded
# in-order listing of (x, y) for y in R_x with y > x (self loops and duplicates vanish in the bitset).
def prog(x):
  (c, es) = x
  (C, L, M) = ltree(c)
  lw = L - mn(L, 4)
  kb = L - lw
  (K, P) = cw(c, 0, zl(L), zl(L), L, M)
  (E, Q) = ew(es, zl(L), zl(L), L, M)
  T = ohs(E, L, lw, kb)
  z = deliver_all(C, Q, L) + deliver_all(T, P, L)
  return addz(fk(K, L, 0, lw, kb, []), z)

# z = 0 once every sink has been applied: the output is released through a switch on it, which keeps the
# deliveries alive (their placeholders feed the output)
def addz(xs, z):
  if z == 0:
    return xs
  else:
    return xs

def cw(xs, i, K, P, L, M):
  match xs:
    case List/Nil:
      return (K, P)
    case List/Cons:
      return cw(xs.tail, i + 1, push(K, xs.head, L, M, $t), push(P, i, L, M, lambda $t: 0), L, M)

def ew(es, E, Q, L, M):
  match es:
    case List/Nil:
      return (E, Q)
    case List/Cons:
      (u, v) = es.head
      E2 = push(push(E, u, L, M, $cv), v, L, M, $cu)
      Q2 = push(push(Q, v, L, M, lambda $cv: 0), u, L, M, lambda $cu: 0)
      return ew(es.tail, E2, Q2, L, M)

# bucket of cluster ids -> bitset
def ohs(E, l, lw, kb):
  switch l:
    case 0:
      return ohl(E, lw, kb)
    case _:
      (a, b) = E
      return (ohs(a, l-1, lw, kb), ohs(b, l-1, lw, kb))

def ohl(xs, lw, kb):
  match xs:
    case List/Nil:
      return zt(lw)
    case List/Cons:
      return ort(oh(xs.head, lw, 1 << (lw + 3)), ohl(xs.tail, lw, kb), lw)

# one-hot word tree (lw word levels, 16-bit words); m = weight of the current top word bit of y
def oh(y, lw, m):
  switch lw:
    case 0:
      return 1 << (y & 15)
    case _:
      if y & m:
        return (zt(lw-1), oh(y, lw-1, m >> 1))
      else:
        return (oh(y, lw-1, m >> 1), zt(lw-1))

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))

def orall(xs, lw):
  match xs:
    case List/Nil:
      return zt(lw)
    case List/Cons:
      return ort(xs.head, orall(xs.tail, lw), lw)

def fk(K, l, x, lw, kb, acc):
  switch l:
    case 0:
      match K:
        case List/Nil:
          return acc
        case List/Cons:
          return em(orall(K, lw), lw, 0, x, acc)
    case _:
      (a, b) = K
      h = 1 << (l-1)
      return fk(a, l-1, x, lw, kb, fk(b, l-1, x + h, lw, kb, acc))

def em(R, lw, base, x, acc):
  switch lw:
    case 0:
      return emw(R, 4, base, x, acc)
    case _:
      (r1, r2) = R
      h = 16 << (lw-1)
      return em(r1, lw-1, base, x, em(r2, lw-1, base + h, x, acc))

def emw(w, k, base, x, acc):
  if w == 0:
    return acc
  else:
    switch k:
      case 0:
        if base > x:
          return List/Cons((x, base), acc)
        else:
          return acc
      case _:
        h = 1 << (k-1)
        return emw(w & ((1 << h) - 1), k-1, base, x, emw(w >> h, k-1, base + h, x, acc))
