# t3_girth: all-sources BFS as ONE bitset frontier loop over pre-wired CHANNELS (after RECON-SWING, expressed
# with Bend's unscoped lambdas): R_v = sources that reached v, F_v = the current frontier (16-bit word trees);
# the edge walk gives both endpoints a (send-binder, receive-end) pair per edge. A round: every vertex sends
# (F, fresh receive-end) on every channel and folds what arrives into a saturating two-counter per bit (no keyed
# routing). In the round for distance k: bit s in F_v and in a neighbour's F -> odd closed walk 2k+1; bit s seen
# twice at a vertex not yet reached -> even closed walk 2k+2. The first detecting round gives the girth
# (standard BFS-from-every-vertex argument); an empty frontier gives 0 (forest). Three rounds in flight.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  S = init(walk(es, zb(l), l, m), l, 0, n, lw)
  (T1, o1, e1, a1, z1) = rnd(S, l, lw)
  (T2, o2, e2, a2, z2) = rnd(T1, l, lw)
  return loop(o1, e1, a1, z1, o2, e2, a2, z2, rnd(T2, l, lw), l, lw, 0)

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

def zw(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zw(l-1), zw(l-1))

def unit(lw, wbase, v):
  switch lw:
    case 0:
      return (wbase == (v >> 4)) << (v & 15)
    case _:
      h = 1 << (lw-1)
      return (unit(lw-1, wbase, v), unit(lw-1, wbase + h, v))

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
      (u, v) = es.head
      return walk(es.tail, pushb(pushb(A, u, l, m, (lambda $x1: 0, $x2)), v, l, m, (lambda $x2: 0, $x1)), l, m)

# leaf: (R, F, channels)
def init(A, l, base, n, lw):
  switch l:
    case 0:
      u = unit(lw, 0, base)
      if base < n:
        return (u, u, A)
      else:
        return (zw(lw), zw(lw), A)
    case _:
      (a1, a2) = A
      h = 1 << (l-1)
      return (init(a1, l-1, base, n, lw), init(a2, l-1, base + h, n, lw))

def orw(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (orw(a1, b1, lw-1), orw(a2, b2, lw-1))

def zp(l):
  switch l:
    case 0:
      return (0, 0)
    case _:
      return (zp(l-1), zp(l-1))

# saturating two-counter per bit: c1 = seen once, c2 = seen at least twice
def c2w(a, b, lw):
  switch lw:
    case 0:
      (a1, a2) = a
      (b1, b2) = b
      return (a1 | b1, a2 | b2 | (a1 & b1))
    case _:
      (x1, x2) = a
      (y1, y2) = b
      return (c2w(x1, y1, lw-1), c2w(x2, y2, lw-1))

def one(f, lw):
  switch lw:
    case 0:
      return (f, 0)
    case _:
      (a, b) = f
      return (one(a, lw-1), one(b, lw-1))

# send F on every channel, gather the two-counter of what arrives
def chan(t, f, lw):
  match t:
    case Br/Leaf:
      return (Br/Leaf, zp(lw), 0)
    case Br/Node:
      (b, u) = t.e
      z = b((f, $n))
      (y, u2) = u
      (l2, yl, zl) = chan(t.l, f, lw)
      (r2, yr, zr) = chan(t.r, f, lw)
      return (Br/Node((lambda $n: 0, u2), l2, r2), c2w(one(y, lw), c2w(yl, yr, lw), lw), z + zl + zr)

# leaf merge over the word trees: returns ((R', F'), odd, even, any)
def mw(r, f, x, lw):
  switch lw:
    case 0:
      (c1, c2) = x
      nr = r ^ 65535
      g = c1 & nr
      return ((r | g, g), (f & c1) != 0, (c2 & nr) != 0, g != 0)
    case _:
      (r1, r2) = r
      (f1, f2) = f
      (x1, x2) = x
      ((ra, fa), oa, ea, aa) = mw(r1, f1, x1, lw-1)
      ((rb, fb), ob, eb, ab) = mw(r2, f2, x2, lw-1)
      return (((ra, rb), (fa, fb)), oa | ob, ea | eb, aa | ab)

# returns (state, odd, even, any, zeros)
def rnd(T, l, lw):
  switch l:
    case 0:
      (r, f, C) = T
      (C2, y, z) = chan(C, f, lw)
      ((r2, f2), o, e, a) = mw(r, f, y, lw)
      return ((r2, f2, C2), o, e, a, z)
    case _:
      (a, b) = T
      (a2, oa, ea, fa, za) = rnd(a, l-1, lw)
      (b2, ob, eb, fb, zb) = rnd(b, l-1, lw)
      return ((a2, b2), oa | ob, ea | eb, fa | fb, za + zb)

# round k processes the frontier at distance k; three rounds in flight when a round's flags decide
def dec(o, e, a, z, k, rest):
  if o:
    return 2 * k + 1
  else:
    if e:
      return 2 * k + 2
    else:
      if a | z:
        return rest
      else:
        return 0

def loop(o, e, a, z, o2, e2, a2, z2, R, l, lw, k):
  (T3, o3, e3, a3, z3) = R
  R4 = rnd(T3, l, lw)
  if ((o | e) == 0) & ((a | z) != 0):
    return loop(o2, e2, a2, z2, o3, e3, a3, z3, R4, l, lw, k + 1)
  else:
    return dec(o, e, a, z, k, 0)
