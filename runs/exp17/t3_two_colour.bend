# t3_two_colour: min-label propagation on the doubled graph H (vertex (v, p) has key 2v+p; edge (u, v) links
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

# (u,0)-(v,1) and (u,1)-(v,0)). Bipartite iff no v has label(2v) = label(2v+1); then colour(v) = label(2v) & 1.
# channel LP core (see t3_cc_label): per undirected edge two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list, keyed pushes that collapse); rounds need no keyed routing; each vertex runs B = 2 rounds
# as a local dataflow loop, then a balanced OR decides, with the next batch spawned before the decision.
def prog(x):
  (n, es) = x
  (l, m) = lvl(2 * n, 0, 1)
  A = walk(es, zoi(l), l, m)
  D = loop(st0(A, l, 0, 2 * n), 1, l, 2)
  if bad(D, l):
    return flatc(l - 1, 0, n, [])
  else:
    return col(D, l, 0, 2 * n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      u0 = 2 * u
      v0 = 2 * v
      A1 = chan(chan(A, u0, v0 + 1, l, m), v0 + 1, u0, l, m)
      return walk(es.tail, chan(chan(A1, u0 + 1, v0, l, m), v0, u0 + 1, l, m), l, m)

def st0(A, lv, base, n):
  switch lv:
    case 0:
      if base < n:
        return (base, A)
      else:
        return (16777215, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n), st0(b, lv-1, base + h, n))

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

def csend(cs, x):
  match cs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      s = cs.head
      z = s((x, $n))
      (rest, zs) = csend(cs.tail, x)
      return (List/Cons(lambda $n: 0, rest), z | zs)

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

# channel u -> v
def chan(A, u, v, l, m):
  return psi(pso(A, u, l, m, lambda $c: 0), v, l, m, $c)
# ---- end channel LP core ----


# leaf pairs ((label(2v), f), (label(2v+1), f)); tail-threaded, so the leaf conses are independent
def col(t, l, base, n2, acc):
  switch l:
    case 0:
      return acc
    case _:
      (a, b) = t
      if l == 1:
        d0 = a
        if base < n2:
          return List/Cons(d0 & 1, acc)
        else:
          return acc
      else:
        h = 1 << (l-1)
        return col(a, l-1, base, n2, col(b, l-1, base + h, n2, acc))

def bad(t, l):
  switch l:
    case 0:
      return 0
    case _:
      (a, b) = t
      if l == 1:
        d0 = a
        d1 = b
        return (d0 == d1) & (d0 < 16777215)
      else:
        return bad(a, l-1) | bad(b, l-1)

def flatc(l, base, n, acc):
  switch l:
    case 0:
      if base < n:
        return List/Cons(16777215, acc)
      else:
        return acc
    case _:
      h = 1 << (l-1)
      return flatc(l-1, base, n, flatc(l-1, base + h, n, acc))
