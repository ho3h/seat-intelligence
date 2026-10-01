# t3_cyclic_vertices: transitive closure by repeated squaring of a bit matrix (no convergence test, so the l
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

# squarings pipeline). C is ONE tuple tree: l levels keyed by vertex, then lw levels keyed by 16-bit word; leaf =
# word. One walk sets the edge bits with keyed ORs (keys known from the input: the chain collapses). A squaring
# step computes for every v: C'_v = C_v | OR_{w in C_v} C_w, by a divide-and-conquer traversal of v's row
# alongside C (bits select rows; rows OR leafwise). After l steps C covers paths of length 1..2^l >= n, so v is
# cyclic iff bit v of C_v is set. The squarings stop early once one changes nothing.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  kb = l - lw
  L = l + lw
  (xx, M) = lvl(1 << L, 0, 1)
  C0 = walk(es, zt(L), lw, L, M)
  C = sqn(C0, l, l, lw, kb)
  return diag(C, l, 0, lw)

def walk(es, C, lw, L, M):
  match es:
    case List/Nil:
      return C
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, ork(C, (u << lw) | (v >> 4), L, M, 1 << (v & 15)), lw, L, M)

# stop early once a squaring changes nothing (closure reached)
def sqn(C, j, l, lw, kb):
  switch j:
    case 0:
      return C
    case _:
      C2 = sq(C, C, l, lw, kb)
      if neq(C, C2, l + lw):
        return sqn(C2, j-1, l, lw, kb)
      else:
        return C2

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

# apply the step to every row of T (vertex levels), each against the whole matrix C
def sq(T, C, lv, lw, kb):
  switch lv:
    case 0:
      return ort(T, sel(T, C, lw, kb, lw), lw)
    case _:
      (a, b) = T
      return (sq(a, C, lv-1, lw, kb), sq(b, C, lv-1, lw, kb))

# OR of the rows of C selected by the bits of row r (r: j word levels; C: j levels of word index, then kb levels)
def sel(r, C, j, kb, lw):
  switch j:
    case 0:
      return selw(r, C, kb, lw)
    case _:
      (r1, r2) = r
      (c1, c2) = C
      return ort(sel(r1, c1, j-1, kb, lw), sel(r2, c2, j-1, kb, lw), lw)

def selw(wd, C, k, lw):
  if wd == 0:
    return zt(lw)
  else:
    switch k:
      case 0:
        return C
      case _:
        (c1, c2) = C
        h = 1 << (k-1)
        return ort(selw(wd & ((1 << h) - 1), c1, k-1, lw), selw(wd >> h, c2, k-1, lw), lw)

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))

def diag(C, lv, base, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (getk(C, base >> 4, lw, mw) >> (base & 15)) & 1
    case _:
      (a, b) = C
      h = 1 << (lv-1)
      return diag(a, lv-1, base, lw) + diag(b, lv-1, base + h, lw)
