# t3_lex_shortest_path: packed labels + frontier Bellman-Ford + a parallel successor pass.
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

# Cost of a path = W*128 + H (weight, then hops; W <= 127000 and H <= 127 fit in 24 bits for n <= 128).
# 1. Shortest packed costs to t by channel label propagation (pre-wired unscoped-lambda channels carrying each
#    edge's cost; 2 local rounds per batch, balanced OR, one-batch lookahead): D(x) = packed cost x -> t.
# 2. One more emission from the final D: every y sends (D(y) + c(y,x), y) to each neighbour x with keyed updates;
#    leaf x keeps the smallest y with D(y) + c = D(x): nxt(x), the lexicographically smallest optimal successor.
# 3. The path is s, nxt(s), ... , t (keyed reads).
def prog(x):
  (n, s, t, es) = x
  if (s >= n) | (t >= n):
    return []
  else:
    if s == t:
      return [s]
    else:
      (l, m) = lvl(n, 0, 1)
      (A, H) = walk(es, zb(l), zoi(l), l, m)
      D = loop(st0(H, l, 0, t), 1, l, 2)
      X = emit2(A, D, l, l, m, pair(D, l))
      (ds, nx) = getk(X, s, l, m)
      if ds == 16777215:
        return []
      else:
        return path(X, s, t, l, m)

def path(X, x, t, l, m):
  if x == t:
    return [t]
  else:
    (d, nx) = getk(X, x, l, m)
    return List/Cons(x, path(X, nx, t, l, m))

def pair(D, l):
  switch l:
    case 0:
      return (D, 16777215)
    case _:
      (a, b) = D
      return (pair(a, l-1), pair(b, l-1))


def walk(es, A, H, l, m):
  match es:
    case List/Nil:
      return (A, H)
    case List/Cons:
      (u, v, w) = es.head
      c = w * 128 + 1
      H2 = chan(chan(H, u, v, c, l, m), v, u, c, l, m)
      return walk(es.tail, pushb(pushb(A, u, l, m, (v, c)), v, l, m, (u, c)), H2, l, m)

def st0(A, lv, base, s):
  switch lv:
    case 0:
      if base == s:
        return (0, A)
      else:
        return (16777215, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, s), st0(b, lv-1, base + h, s))





# successor pass: keyed update of leaf (D(x), nxt) with candidate (cost, y)
def nxk(t, k, l, m, cst, y):
  switch l:
    case 0:
      (d, nx) = t
      hit = (cst == d) & (y < nx)
      return (d, nx - hit * (nx - y))
    case _:
      (a, b) = t
      if k & m:
        return (a, nxk(b, k, l-1, m >> 1, cst, y))
      else:
        return (nxk(a, k, l-1, m >> 1, cst, y), b)

def eb2(t, d, y, X, l, m):
  match t:
    case Br/Leaf:
      return X
    case Br/Node:
      (v, c) = t.e
      return eb2(t.r, d, y, eb2(t.l, d, y, nxk(X, v, l, m, d + c, y), l, m), l, m)

def emit2(A, D, l, lv, m, X):
  return emit2g(A, D, l, lv, m, X, 0)

def emit2g(A, D, l, lv, m, X, base):
  switch lv:
    case 0:
      d = D
      if d < 16777215:
        return eb2(A, d, base, X, l, m)
      else:
        return X
    case _:
      (a1, a2) = A
      (d1, d2) = D
      h = 1 << (lv-1)
      return emit2g(a2, d2, l, lv-1, m, emit2g(a1, d1, l, lv-1, m, X, base), base + h)

# ---- channel LP core: per vertex (label, (outs, ins)); outs = senders, ins = receivers ----
def lpq(A, l, m, s0):
  return loop(s0, 1, l, 2)

def loop(S, any, l, B):
  (S2, Lin, any2) = rall(S, l, B)
  if any:
    return loop(S2, any2, l, B)
  else:
    return Lin

def rall(S, lv, B):
  switch lv:
    case 0:
      (x, oi) = S
      (os, ins) = oi
      (x2, os2, ins2, ch) = vrun(x, os, ins, B, 0)
      return ((x2, (os2, ins2)), x, ch)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, B)
      (b2, lb, fb) = rall(b, lv-1, B)
      return ((a2, b2), (la, lb), fa | fb)

def vrun(x, os, ins, B, ch):
  switch B:
    case 0:
      return (x, os, ins, ch)
    case _:
      (os2, z) = csend(os, x)
      (ins2, my) = crecv(ins)
      x2 = mn(x, my)
      return vrun(x2, os2, ins2, B-1, (x2 < x) | z)

# out-channel elements carry their packed edge cost c
def csend(cs, x):
  match cs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      (s, c) = cs.head
      z = s((x + (x < 16777215) * c, $n))
      (rest, zs) = csend(cs.tail, x)
      return (List/Cons((lambda $n: 0, c), rest), z | zs)

def crecv(cs):
  match cs:
    case List/Nil:
      return ([], 16777215)
    case List/Cons:
      (y, r2) = cs.head
      (rest, my) = crecv(cs.tail)
      return (List/Cons(r2, rest), mn(y, my))

# push a sender to u's outs and the matching receiver to v's ins (both keyed pushes; keys are input data)
def pso(t, k, l, m, v):
  switch l:
    case 0:
      (os, ins) = t
      return (List/Cons(v, os), ins)
    case _:
      (a, b) = t
      if k & m:
        return (a, pso(b, k, l-1, m >> 1, v))
      else:
        return (pso(a, k, l-1, m >> 1, v), b)

def psi(t, k, l, m, v):
  switch l:
    case 0:
      (os, ins) = t
      return (os, List/Cons(v, ins))
    case _:
      (a, b) = t
      if k & m:
        return (a, psi(b, k, l-1, m >> 1, v))
      else:
        return (psi(a, k, l-1, m >> 1, v), b)

def zoi(l):
  switch l:
    case 0:
      return ([], [])
    case _:
      return (zoi(l-1), zoi(l-1))

# channel u -> v with cost w
def chan(A, u, v, w, l, m):
  return psi(pso(A, u, l, m, (lambda $c: 0, w)), v, l, m, $c)
# ---- end channel LP core ----
