# t5_cluster_histogram: component labels (below), then a scatter of 1 per vertex into a size tree keyed by
# final label (keyed adds, collapse once labels exist), then a balanced reduction of one-hot 8-vectors.
# Components: min-label propagation over pre-wired CHANNELS (after RECON-SWING, expressed with Bend's unscoped
# lambdas): the edge walk gives each endpoint a (send-binder, receive-end) pair per edge in a Braun tree at its
# leaf; a round sends (label, fresh receive-end) through every binder and reads (y, next receive-end) from every
# receive-end (no keyed routing), new label = min; rounds repeat while a label changed, with three rounds in
# flight when the OR-reduce decides.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (A, ne) = walk(es, zb(l), l, m, 0)
  S = scat(cc(A, l, n), l, 0, n, l, m, zt(l))
  (a, b, c, d, e, f, g, h) = hist(S, l)
  return [a, b, c, d, e, f, g, h]

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def add(t, k, l, m, v):
  switch l:
    case 0:
      return t + v
    case _:
      (a, b) = t
      if k & m:
        return (a, add(b, k, l-1, m >> 1, v))
      else:
        return (add(a, k, l-1, m >> 1, v), b)

def scat(D, lv, base, n, l, m, S):
  switch lv:
    case 0:
      return add(S, D, l, m, base < n)
    case _:
      (d1, d2) = D
      h = 1 << (lv-1)
      return scat(d2, lv-1, base + h, n, l, m, scat(d1, lv-1, base, n, l, m, S))

def hist(S, l):
  switch l:
    case 0:
      return (S == 1, S == 2, S == 3, S == 4, S == 5, S == 6, S == 7, S >= 8)
    case _:
      (x, y) = S
      (a1, b1, c1, d1, e1, f1, g1, h1) = hist(x, l-1)
      (a2, b2, c2, d2, e2, f2, g2, h2) = hist(y, l-1)
      return (a1 + a2, b1 + b2, c1 + c2, d1 + d2, e1 + e2, f1 + f2, g1 + g2, h1 + h2)

type Br:
  Node { e, l, r }
  Leaf


def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

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

def walk(es, A, l, m, c):
  match es:
    case List/Nil:
      return (A, c)
    case List/Cons:
      (u, v) = es.head
      A2 = pushb(pushb(A, u, l, m, (lambda $x1: 0, $x2)), v, l, m, (lambda $x2: 0, $x1))
      return walk(es.tail, A2, l, m, c + 1)

def init(A, l, base, n):
  switch l:
    case 0:
      return (base | ((base >= n) * 16777215), A)
    case _:
      (a, b) = A
      h = 1 << (l-1)
      return (init(a, l-1, base, n), init(b, l-1, base + h, n))

def mn(a, b):
  return a + (b < a) * (b - a)

# one round on a vertex's channel tree: send v everywhere, receive the neighbours' values
# returns (new channel tree, min received, sum of the zeros the sends returned)
def chan(t, v):
  match t:
    case Br/Leaf:
      return (Br/Leaf, 16777215, 0)
    case Br/Node:
      (b, u) = t.e
      z = b((v, $n))
      (y, u2) = u
      (l2, ml, zl) = chan(t.l, v)
      (r2, mr, zr) = chan(t.r, v)
      return (Br/Node((lambda $n: 0, u2), l2, r2), mn(y, mn(ml, mr)), z + zl + zr)

# returns (new state tree, changed?, zeros, label tree as plain numbers)
def rnd(T, l):
  switch l:
    case 0:
      (v, C) = T
      (C2, y, z) = chan(C, v)
      t = y < v
      v2 = v + t * (y - v)
      return ((v2, C2), t, z, v2)
    case _:
      (a, b) = T
      (a2, fa, za, la) = rnd(a, l-1)
      (b2, fb, zb, lb) = rnd(b, l-1)
      return ((a2, b2), fa | fb, za + zb, (la, lb))

# three rounds are in flight when the OR-reduce of a round decides (three-round lookahead)
def loop(any, z, L, a2, z2, L2, a3, z3, L3, a4, z4, L4, R, l):
  (T5, a5, z5, L5) = R
  R6 = rnd(T5, l)
  if any | z:
    return loop(a2, z2, L2, a3, z3, L3, a4, z4, L4, a5, z5, L5, R6, l)
  else:
    return L

# final min labels (plain number tree) of the components, 3 rounds in flight
def cc(A, l, n):
  (T1, a1, z1, L1) = rnd(init(A, l, 0, n), l)
  (T2, a2, z2, L2) = rnd(T1, l)
  (T3, a3, z3, L3) = rnd(T2, l)
  (T4, a4, z4, L4) = rnd(T3, l)
  return loop(a1, z1, L1, a2, z2, L2, a3, z3, L3, a4, z4, L4, rnd(T4, l), l)
