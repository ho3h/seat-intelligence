# t3_cheapest_k_walk: k fixed-count (min, +) rounds over pre-wired CHANNELS (after RECON-SWING, expressed with
# Bend's unscoped lambdas): the edge walk gives u a send-binder and v the matching (receive-end, w) for each arc
# u -> v (Braun trees at their leaves). A round: every vertex sends (d, fresh receive-end) through its binders
# and takes the min of y + w over what arrives (no keyed routing). There is no convergence test, so rounds
# pipeline: round r+1's structure expands while round r's numbers still flow.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, s, t, k, es) = x
  if (s >= n) | (t >= n):
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    (O, I) = walk(es, zb(l), zb(l), l, m)
    (T, z) = rounds(init(O, I, l, 0, s), l, k)
    return z + getd(T, t, l, m)

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

def walk(es, O, I, l, m):
  match es:
    case List/Nil:
      return (O, I)
    case List/Cons:
      (u, v, w) = es.head
      return walk(es.tail, pushb(O, u, l, m, lambda $x: 0), pushb(I, v, l, m, ($x, w)), l, m)

def init(O, I, l, base, s):
  switch l:
    case 0:
      return ((base != s) * 16777215, O, I)
    case _:
      (o1, o2) = O
      (i1, i2) = I
      h = 1 << (l-1)
      return (init(o1, i1, l-1, base, s), init(o2, i2, l-1, base + h, s))

def mn(a, b):
  return a + (b < a) * (b - a)

def send(t, d):
  match t:
    case Br/Leaf:
      return (Br/Leaf, 0)
    case Br/Node:
      b = t.e
      z = b((d, $n))
      (l2, zl) = send(t.l, d)
      (r2, zr) = send(t.r, d)
      return (Br/Node(lambda $n: 0, l2, r2), z + zl + zr)

def recv(t):
  match t:
    case Br/Leaf:
      return (Br/Leaf, 16777215)
    case Br/Node:
      (u, w) = t.e
      (y, u2) = u
      (l2, yl) = recv(t.l)
      (r2, yr) = recv(t.r)
      return (Br/Node((u2, w), l2, r2), mn((y + w) | ((y == 16777215) * 16777215), mn(yl, yr)))

def rnd(T, l):
  switch l:
    case 0:
      (d, O, I) = T
      (O2, z) = send(O, d)
      (I2, y) = recv(I)
      return ((y, O2, I2), z)
    case _:
      (a, b) = T
      (a2, za) = rnd(a, l-1)
      (b2, zb) = rnd(b, l-1)
      return ((a2, b2), za + zb)

def rounds(T, l, k):
  switch k:
    case 0:
      return (T, 0)
    case _:
      (T2, z) = rnd(T, l)
      (T3, z2) = rounds(T2, l, k-1)
      return (T3, z + z2)

def getd(t, k, l, m):
  switch l:
    case 0:
      (d, O, I) = t
      return d
    case _:
      (a, b) = t
      if k & m:
        return getd(b, k, l-1, m >> 1)
      else:
        return getd(a, k, l-1, m >> 1)
