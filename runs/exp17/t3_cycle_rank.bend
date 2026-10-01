# t3_cycle_rank = m - n + c. Components by min-label propagation over pre-wired CHANNELS (after RECON-SWING,
# expressed with Bend's unscoped lambdas): the edge walk creates, per edge, two one-shot wires (lambda $x: 0
# and its variable) and hands each endpoint a (send-binder, receive-end) pair in a Braun tree at its leaf.
# A round: every vertex sends (label, fresh receive-end) through each binder and reads (y, next receive-end)
# from each receive-end, so a message costs one application, with no keyed routing at all; the new label is
# the min. Rounds repeat while some label changed (OR-reduce). c = number of vertices whose label is their id.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (A, ne) = walk(es, zb(l), l, m, 0)
  (T1, a1, z1, L1) = rnd(init(A, l, 0, n), l)
  (T2, a2, z2, L2) = rnd(T1, l)
  T = loop(a1, z1, L1, a2, z2, L2, rnd(T2, l), l)
  return ne + roots(T, l, 0, n) - n

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
def loop(any, z, L, a2, z2, L2, R, l):
  (T3, a3, z3, L3) = R
  R4 = rnd(T3, l)
  if any | z:
    return loop(a2, z2, L2, a3, z3, L3, R4, l)
  else:
    return L

def roots(T, l, base, n):
  switch l:
    case 0:
      v = T
      return (v == base) & (base < n)
    case _:
      (a, b) = T
      h = 1 << (l-1)
      return roots(a, l-1, base, n) + roots(b, l-1, base + h, n)
