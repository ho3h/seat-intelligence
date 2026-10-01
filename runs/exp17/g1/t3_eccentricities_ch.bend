# t3_eccentricities: all-sources BFS as bitset rows exchanged over pre-wired channels. Rows are word trees
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

# (16-bit words). Per undirected edge the walk creates two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list; keyed pushes that collapse). A round: every vertex sends its ball R_v (and a fresh
# `lambda $next` becomes the channel's next sender) and ORs the rows it receives: R'_v = R_v | OR R_u. No keyed
# routing and no copying of the whole matrix per vertex. ecc(v) = number of rounds in which R_v was not yet full.
# Each vertex runs 2 local rounds per batch; a balanced OR of "some ball not full" decides, with the next batch
# spawned before the decision (one-batch lookahead).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  H = walk(es, zoi(l), l, m)
  F = full(lw, 0, n)
  S0 = st0(H, l, 0, n, lw)
  E = loop(S0, 1, l, F, lw)
  return flat(E, l, 0, n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(chan(A, u, v, l, m), v, u, l, m), l, m)

def st0(A, lv, base, n, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (ork(zt(lw), base >> 4, lw, mw, (base < n) << (base & 15)), 0, base < n, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n, lw), st0(b, lv-1, base + h, n, lw))

def loop(S, any, l, F, lw):
  (S2, Ein, any2) = rall(S, l, F, lw)
  if any:
    return loop(S2, any2, l, F, lw)
  else:
    return Ein

def rall(S, lv, F, lw):
  switch lv:
    case 0:
      (R, E, real, oi) = S
      (os, ins) = oi
      (R2, E2, os2, ins2, nf) = vrun(R, E, real, os, ins, 2, F, lw)
      return ((R2, E2, real, (os2, ins2)), E, nf)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, F, lw)
      (b2, lb, fb) = rall(b, lv-1, F, lw)
      return ((a2, b2), (la, lb), fa | fb)

# nf of the returned state = its ball is still not full
def vrun(R, E, real, os, ins, B, F, lw):
  nf = real & neq(R, F, lw)
  switch B:
    case 0:
      return (R, E, os, ins, nf)
    case _:
      (os2, z) = csend(os, R)
      (ins2, got) = crecv(ins, lw)
      return vrun(ort(R, got, lw), E + nf + z, real, os2, ins2, B-1, F, lw)

def csend(cs, x):
  match cs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      s = cs.head
      z = s((x, $n))
      (rest, zs) = csend(cs.tail, x)
      return (List/Cons(lambda $n: 0, rest), z | zs)

def crecv(cs, lw):
  match cs:
    case List/Nil:
      return ([], zt(lw))
    case List/Cons:
      (y, r2) = cs.head
      (rest, my) = crecv(cs.tail, lw)
      return (List/Cons(r2, rest), ort(y, my, lw))

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

def chan(A, u, v, l, m):
  return psi(pso(A, u, l, m, lambda $c: 0), v, l, m, $c)

def full(lw, base, n):
  switch lw:
    case 0:
      k = n - mn(n, base)
      return (1 << mn(k, 16)) - 1
    case _:
      h = 16 << (lw-1)
      return (full(lw-1, base, n), full(lw-1, base + h, n))

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))
