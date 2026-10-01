# t3_articulation_points: n searches as ONE bitset frontier loop. Bit v = "search in G - v, started at v's
# smallest neighbour". R_u starts as {u} (so u blocks its own search and never propagates it) plus the bits
# of the searches that start at u. Rounds run over pre-wired CHANNELS (after RECON-SWING, expressed with Bend's
# unscoped lambdas): the edge walk gives both endpoints a (send-binder, receive-end) pair per edge; a round sends
# (F, fresh receive-end) on every channel and ORs what arrives (no keyed routing), F' = N & ~R, R' = R | F',
# until nothing is new (three rounds in flight when the OR-reduce decides).
# v is a cut vertex iff some neighbour u of v is not reached by search v: cut set = OR_u (Nb_u & ~R_u),
# listed ascending by a right-to-left traversal that threads the tail.
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  L = l + lw
  (A, MN, NB) = walk(es, zb(l), zinf(l), zw(L), l, m, L, top(L), lw)
  (R0, F0) = start(MN, l, 0, l, m, lw, init(l, 0, n, lw), zw(L))
  S = zipd(R0, F0, A, l)
  (T1, a1, z1, L1) = rnd(S, l, lw)
  (T2, a2, z2, L2) = rnd(T1, l, lw)
  D = loop(a1, z1, L1, a2, z2, L2, rnd(T2, l, lw), l, lw)
  C = cut(D, NB, l, lw)
  return bits(C, lw, 0, [])

def top(L):
  switch L:
    case 0:
      return 0
    case _:
      return 1 << L-1

def zinf(l):
  switch l:
    case 0:
      return 16777215
    case _:
      return (zinf(l-1), zinf(l-1))

def updmin(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmin(b, k, l-1, m >> 1, x))
      else:
        return (updmin(a, k, l-1, m >> 1, x), b)

def setb(t, k, l, m, bit):
  switch l:
    case 0:
      return t | bit
    case _:
      (a, b) = t
      if k & m:
        return (a, setb(b, k, l-1, m >> 1, bit))
      else:
        return (setb(a, k, l-1, m >> 1, bit), b)

# search v starts at v's smallest neighbour a: bit v goes into R_a and F_a (keyed OR-updates, keys = data)
def start(MN, lv, base, l, m, lw, R, F):
  switch lv:
    case 0:
      if MN == 16777215:
        return (R, F)
      else:
        u = unit(lw, 0, base)
        return (upd(R, MN, l, m, u, lw), upd(F, MN, l, m, u, lw))
    case _:
      (a, b) = MN
      h = 1 << (lv-1)
      (R1, F1) = start(a, lv-1, base, l, m, lw, R, F)
      return start(b, lv-1, base + h, l, m, lw, R1, F1)

def zipd(R, F, A, l):
  switch l:
    case 0:
      return (R, F, A)
    case _:
      (r1, r2) = R
      (f1, f2) = F
      (a1, a2) = A
      return (zipd(r1, f1, a1, l-1), zipd(r2, f2, a2, l-1))

def andn(a, r, lw):
  switch lw:
    case 0:
      return a & (r ^ 65535)
    case _:
      (a1, a2) = a
      (r1, r2) = r
      return (andn(a1, r1, lw-1), andn(a2, r2, lw-1))

# OR over u of (Nb_u & ~R_u): bit v set iff some neighbour u of v was not reached by search v
def cut(D, NB, l, lw):
  switch l:
    case 0:
      return andn(NB, D, lw)
    case _:
      (d1, d2) = D
      (b1, b2) = NB
      return orw(cut(d1, b1, l-1, lw), cut(d2, b2, l-1, lw), lw)

def bits(C, lw, wbase, tl):
  switch lw:
    case 0:
      return wbits(C, wbase * 16, 16, tl)
    case _:
      (a, b) = C
      h = 1 << (lw-1)
      return bits(a, lw-1, wbase, bits(b, lw-1, wbase + h, tl))

def wbits(w, base, k, tl):
  switch k:
    case 0:
      return tl
    case _:
      i = k - 1
      if (w >> i) & 1:
        return wbits(w, base, i, List/Cons(base + i, tl))
      else:
        return wbits(w, base, i, tl)

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

# word tree with only bit v set (v < 16 * 2^lw); wbase = index of the first word of this subtree
def unit(lw, wbase, v):
  switch lw:
    case 0:
      return (wbase == (v >> 4)) << (v & 15)
    case _:
      h = 1 << (lw-1)
      return (unit(lw-1, wbase, v), unit(lw-1, wbase + h, v))

def init(l, base, n, lw):
  switch l:
    case 0:
      if base < n:
        return unit(lw, 0, base)
      else:
        return zw(lw)
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, n, lw), init(l-1, base + h, n, lw))

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

def walk(es, A, MN, NB, l, m, L, M, lw):
  match es:
    case List/Nil:
      return (A, MN, NB)
    case List/Cons:
      (u, v) = es.head
      A2 = pushb(pushb(A, u, l, m, (lambda $x1: 0, $x2)), v, l, m, (lambda $x2: 0, $x1))
      MN2 = updmin(updmin(MN, u, l, m, v), v, l, m, u)
      NB2 = setb(setb(NB, (u << lw) | (v >> 4), L, M, 1 << (v & 15)), (v << lw) | (u >> 4), L, M, 1 << (u & 15))
      return walk(es.tail, A2, MN2, NB2, l, m, L, M, lw)

def orw(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (orw(a1, b1, lw-1), orw(a2, b2, lw-1))

def upd(t, k, l, m, x, lw):
  switch l:
    case 0:
      return orw(t, x, lw)
    case _:
      (a, b) = t
      if k & m:
        return (a, upd(b, k, l-1, m >> 1, x, lw))
      else:
        return (upd(a, k, l-1, m >> 1, x, lw), b)

def chan(t, f, lw):
  match t:
    case Br/Leaf:
      return (Br/Leaf, zw(lw), 0)
    case Br/Node:
      (b, u) = t.e
      z = b((f, $n))
      (y, u2) = u
      (l2, yl, zl) = chan(t.l, f, lw)
      (r2, yr, zr) = chan(t.r, f, lw)
      return (Br/Node((lambda $n: 0, u2), l2, r2), orw(y, orw(yl, yr, lw), lw), z + zl + zr)

# leaf merge over the word trees: returns ((R', F'), any)
def mw(r, x, lw):
  switch lw:
    case 0:
      f = x & (r ^ 65535)
      return ((r | f, f), f != 0)
    case _:
      (r1, r2) = r
      (x1, x2) = x
      ((ra, fa), aa) = mw(r1, x1, lw-1)
      ((rb, fb), ab) = mw(r2, x2, lw-1)
      return (((ra, rb), (fa, fb)), aa | ab)

# returns (state, any, zeros, R tree as plain numbers)
def rnd(T, l, lw):
  switch l:
    case 0:
      (r, f, C) = T
      (C2, y, z) = chan(C, f, lw)
      ((r2, f2), a) = mw(r, y, lw)
      return ((r2, f2, C2), a, z, r2)
    case _:
      (a, b) = T
      (a2, fa, za, ra) = rnd(a, l-1, lw)
      (b2, fb, zb, rb) = rnd(b, l-1, lw)
      return ((a2, b2), fa | fb, za + zb, (ra, rb))

def loop(any, z, L, a2, z2, L2, R, l, lw):
  (T3, a3, z3, L3) = R
  R4 = rnd(T3, l, lw)
  if any | z:
    return loop(a2, z2, L2, a3, z3, L3, R4, l, lw)
  else:
    return L
