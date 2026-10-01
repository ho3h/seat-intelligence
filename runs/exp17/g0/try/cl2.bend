# t3_closure_size: all-sources BFS as ONE bitset frontier loop over pre-wired CHANNELS (after RECON-SWING,
# expressed with Bend's unscoped lambdas). Every vertex v keeps R_v (sources that reach v) and F_v (sources that
# reached v last round) as trees of 16-bit words. The edge walk gives u a send-binder and v the matching
# receive-end for each arc u -> v (Braun trees at their leaves). A round: every vertex sends (F, fresh
# receive-end) through its binders and ORs what arrives at its receive-ends (no keyed routing); F' = N & ~R,
# R' = R | F'. Rounds repeat while anything is new, three rounds in flight when the OR-reduce decides.
# Answer: sum of popcount(R_v) minus n (v reaches itself trivially), summed on the way up each round.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  (O, I) = walk(es, zb(l), zb(l), l, m)
  S = init(O, I, l, 0, n, lw)
  (T1, a1, z1, L1) = rnd(S, l, lw)
  (T2, a2, z2, L2) = rnd(T1, l, lw)
  return loop(a1, z1, L1, a2, z2, L2, rnd(T2, l, lw), l, lw) - n

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

def walk(es, O, I, l, m):
  match es:
    case List/Nil:
      return (O, I)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, pushb(O, u, l, m, lambda $x: 0), pushb(I, v, l, m, $x), l, m)

# leaf: (R, F, out-binders, in-ends)
def init(O, I, l, base, n, lw):
  switch l:
    case 0:
      u = unit(lw, 0, base) 
      if base < n:
        return (u, u, O, I)
      else:
        return (zw(lw), zw(lw), O, I)
    case _:
      (o1, o2) = O
      (i1, i2) = I
      h = 1 << (l-1)
      return (init(o1, i1, l-1, base, n, lw), init(o2, i2, l-1, base + h, n, lw))

def orw(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (orw(a1, b1, lw-1), orw(a2, b2, lw-1))

def send(t, f):
  match t:
    case Br/Leaf:
      return (Br/Leaf, 0)
    case Br/Node:
      b = t.e
      z = b((f, $n))
      (l2, zl) = send(t.l, f)
      (r2, zr) = send(t.r, f)
      return (Br/Node(lambda $n: 0, l2, r2), z + zl + zr)

def recv(t, lw):
  match t:
    case Br/Leaf:
      return (Br/Leaf, zw(lw))
    case Br/Node:
      (y, u2) = t.e
      (l2, yl) = recv(t.l, lw)
      (r2, yr) = recv(t.r, lw)
      return (Br/Node(u2, l2, r2), orw(y, orw(yl, yr, lw), lw))

# leaf merge over the word trees: returns ((R', F'), any, popcount R')
def mw(r, x, lw):
  switch lw:
    case 0:
      f = x & (r ^ 65535)
      r2 = r | f
      return ((r2, f), f != 0, popc(r2))
    case _:
      (r1, r2) = r
      (x1, x2) = x
      ((ra, fa), aa, ca) = mw(r1, x1, lw-1)
      ((rb, fb), ab, cb) = mw(r2, x2, lw-1)
      return (((ra, rb), (fa, fb)), aa | ab, ca + cb)

def rnd(T, l, lw):
  switch l:
    case 0:
      (r, f, O, I) = T
      (O2, z) = send(O, f)
      (I2, y) = recv(I, lw)
      ((r2, f2), a, c) = mw(r, y, lw)
      return ((r2, f2, O2, I2), a, z, c)
    case _:
      (a, b) = T
      (a2, fa, za, ca) = rnd(a, l-1, lw)
      (b2, fb, zb, cb) = rnd(b, l-1, lw)
      return ((a2, b2), fa | fb, za + zb, ca + cb)

def loop(any, z, L, a2, z2, L2, R, l, lw):
  (T3, a3, z3, L3) = R
  R4 = rnd(T3, l, lw)
  if any | z:
    return loop(a2, z2, L2, a3, z3, L3, R4, l, lw)
  else:
    return L

def popc(x):
  a = x - ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b + (b >> 4)) & 3855
  return (c + (c >> 8)) & 31
