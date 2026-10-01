# t3_cheapest_k_walk: k fixed-count (min, +) rounds over pre-wired CHANNELS (after RECON-SWING, expressed with
# Bend's unscoped lambdas). A channel is a send-binder at its tail and a (receive-end, weight) at its head
# (Braun trees at their leaves). A round: every vertex sends (d, fresh receive-end) through its binders and
# takes the min of y + w over what arrives (no keyed routing). There is no convergence test, so rounds
# pipeline. To halve the number of rounds, a second channel set is wired once per 2-arc walk u -> v -> x
# (weight w1 + w2, built at every v from its in- and out-arc lists by keyed pushes): k = 2j + (k & 1) is
# done as (k & 1) one-arc rounds and j two-arc rounds.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, s, t, k, es) = x
  if (s >= n) | (t >= n):
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    (O, I, IN, OUT) = walk(es, zb(l), zb(l), zb(l), zb(l), l, m)
    (O2, I2) = pairs(IN, OUT, l, l, m, zb(l), zb(l))
    (T1, z1) = rounds(init(O, I, l, 0, s), l, k & 1)
    (T, z) = rounds(recable(T1, O2, I2, l), l, k >> 1)
    return z1 + z + getd(T, t, l, m)

# swap the one-arc channels for the two-arc ones (the unused one-arc channels are erased)
def recable(T, O, I, l):
  switch l:
    case 0:
      (d, o, i) = T
      return (d, O, I)
    case _:
      (a, b) = T
      (o1, o2) = O
      (i1, i2) = I
      return (recable(a, o1, i1, l-1), recable(b, o2, i2, l-1))

# at every v: one channel per (in-arc (u, w1), out-arc (x, w2)): binder to u, (end, w1 + w2) to x
def pairs(IN, OUT, lv, l, m, O, I):
  switch lv:
    case 0:
      return pin(IN, OUT, l, m, O, I)
    case _:
      (a1, a2) = IN
      (b1, b2) = OUT
      (O1, I1) = pairs(a1, b1, lv-1, l, m, O, I)
      return pairs(a2, b2, lv-1, l, m, O1, I1)

def pin(IN, OUT, l, m, O, I):
  match IN:
    case Br/Leaf:
      return (O, I)
    case Br/Node:
      (u, w1) = IN.e
      (O1, I1) = pout(OUT, u, w1, l, m, O, I)
      (O2, I2) = pin(IN.l, OUT, l, m, O1, I1)
      return pin(IN.r, OUT, l, m, O2, I2)

def pout(OUT, u, w1, l, m, O, I):
  match OUT:
    case Br/Leaf:
      return (O, I)
    case Br/Node:
      (x, w2) = OUT.e
      O1 = pushb(O, u, l, m, lambda $c: 0)
      I1 = pushb(I, x, l, m, ($c, w1 + w2))
      (O2, I2) = pout(OUT.l, u, w1, l, m, O1, I1)
      return pout(OUT.r, u, w1, l, m, O2, I2)

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

def walk(es, O, I, IN, OUT, l, m):
  match es:
    case List/Nil:
      return (O, I, IN, OUT)
    case List/Cons:
      (u, v, w) = es.head
      O2 = pushb(O, u, l, m, lambda $x: 0)
      I2 = pushb(I, v, l, m, ($x, w))
      return walk(es.tail, O2, I2, pushb(IN, v, l, m, (u, w)), pushb(OUT, u, l, m, (v, w)), l, m)

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
