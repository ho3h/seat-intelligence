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

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v, w) = es.head
      A2 = pushb(pushb(A, u, l, m, (lambda $x1: 0, $x2, w)), v, l, m, (lambda $x2: 0, $x1, w))
      return walk(es.tail, A2, l, m)

def init(A, l, base, s):
  switch l:
    case 0:
      return ((base != s) * 16777215, A)
    case _:
      (a, b) = A
      h = 1 << (l-1)
      return (init(a, l-1, base, s), init(b, l-1, base + h, s))

def mn(a, b):
  return a + (b < a) * (b - a)

# one round on a vertex's channel tree: send v everywhere, receive the neighbours' values
# returns (new channel tree, min received, sum of the zeros the sends returned)
def chan(t, v):
  match t:
    case Br/Leaf:
      return (Br/Leaf, 16777215, 0)
    case Br/Node:
      (b, u, w) = t.e
      z = b((v, $n))
      (y, u2) = u
      (l2, ml, zl) = chan(t.l, v)
      (r2, mr, zr) = chan(t.r, v)
      return (Br/Node((lambda $n: 0, u2, w), l2, r2), mn(CAND, mn(ml, mr)), z + zl + zr)

# returns (new state tree, changed?, zeros, label tree as plain numbers)
def rnd(T, l, bud):
  switch l:
    case 0:
      (v, C) = T
      (C2, y, z) = chan(C, v)
      t = (y < v) & (y <= bud)
      v2 = v + t * (y - v)
      return ((v2, C2), t, z, v2)
    case _:
      (a, b) = T
      (a2, fa, za, la) = rnd(a, l-1, bud)
      (b2, fb, zb, lb) = rnd(b, l-1, bud)
      return ((a2, b2), fa | fb, za + zb, (la, lb))

# three rounds are in flight when the OR-reduce of a round decides (three-round lookahead)
def loop(any, z, L, a2, z2, L2, R, l, bud):
  (T3, a3, z3, L3) = R
  R4 = rnd(T3, l, bud)
  if any | z:
    return loop(a2, z2, L2, a3, z3, L3, R4, l, bud)
  else:
    return L

# final distances (plain number tree), 3 rounds in flight
def sssp(A, l, s, bud):
  (T1, a1, z1, L1) = rnd(init(A, l, 0, s), l, bud)
  (T2, a2, z2, L2) = rnd(T1, l, bud)
  return loop(a1, z1, L1, a2, z2, L2, rnd(T2, l, bud), l, bud)
