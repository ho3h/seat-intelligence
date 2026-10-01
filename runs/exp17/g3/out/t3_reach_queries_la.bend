# t3_reach_queries: transitive closure by repeated squaring of a bit matrix, l = ceil(log2 n) fixed rounds
# (no convergence test between rounds, so round k+1's structure expands while round k's words still flow).
# M: trie over rows (l levels) then 16-bit words (lw levels). Built during the edge walk with keyed OR updates
# from an identity trie. Squaring: row v = OR over u of (bit u of row v ? row u : 0), by a balanced traversal
# (row words aligned with the u-trie's upper levels, bits within a word with its lower 4 levels) and a
# balanced OR reduction (4 rows fused per word traversal; all-zero words skip their 16 rows). Queries are answered by keyed word reads while the query list is walked.
# ---- base: tuple tries keyed by vertex id (MSB first), l levels, m = top-bit mask
type Br:
  Node { e, l, r }
  Leaf

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l, z):
  switch l:
    case 0:
      return z
    case _:
      return (zt(l-1, z), zt(l-1, z))

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

def inc(t, k, l, m):
  switch l:
    case 0:
      return t + 1
    case _:
      (a, b) = t
      if k & m:
        return (a, inc(b, k, l-1, m >> 1))
      else:
        return (inc(a, k, l-1, m >> 1), b)

def get(t, k, l, m):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      if k & m:
        return get(b, k, l-1, m >> 1)
      else:
        return get(a, k, l-1, m >> 1)

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

def updmax(t, k, l, m, x):
  switch l:
    case 0:
      return t + (x > t) * (x - t)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmax(b, k, l-1, m >> 1, x))
      else:
        return (updmax(a, k, l-1, m >> 1, x), b)
def prog(x):
  (n, qs, es) = x
  (l, m) = lvl(n, 0, 1)
  lb = l - (l > 4) * (l - 4)
  lw = l - lb
  mk = m << lw
  M0 = walk(es, idm(l, lw, 0), l + lw, mk, lw)
  M = sqn(M0, sq(M0, M0, l, l, lw, lb), l, lw, lb)
  return answer(qs, M, l + lw, mk, lw)

def idrow(lw, wi, t, b):
  switch lw:
    case 0:
      return (wi == t) * b
    case _:
      h = 1 << (lw-1)
      return (idrow(lw-1, wi, t, b), idrow(lw-1, wi + h, t, b))

def idm(l, lw, base):
  switch l:
    case 0:
      return idrow(lw, 0, base >> 4, 1 << (base & 15))
    case _:
      h = 1 << (l-1)
      return (idm(l-1, lw, base), idm(l-1, lw, base + h))

def orb(t, k, l, m, b):
  switch l:
    case 0:
      return t | b
    case _:
      (a, c) = t
      if k & m:
        return (a, orb(c, k, l-1, m >> 1, b))
      else:
        return (orb(a, k, l-1, m >> 1, b), c)

def walk(es, M, L, mk, lw):
  match es:
    case List/Nil:
      return M
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, orb(M, (u << lw) | (v >> 4), L, mk, 1 << (v & 15)), L, mk, lw)

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))

def rowm(r, k, lw):
  switch lw:
    case 0:
      return r & k
    case _:
      (a, b) = r
      return (rowm(a, k, lw-1), rowm(b, k, lw-1))

def o4(r0, r1, r2, r3, k0, k1, k2, k3, lw):
  switch lw:
    case 0:
      return (r0 & k0) | (r1 & k1) | (r2 & k2) | (r3 & k3)
    case _:
      (a0, b0) = r0
      (a1, b1) = r1
      (a2, b2) = r2
      (a3, b3) = r3
      return (o4(a0, a1, a2, a3, k0, k1, k2, k3, lw-1), o4(b0, b1, b2, b3, k0, k1, k2, k3, lw-1))

# OR of the rows of Ms (2^lv rows) whose bit in w (from pos) is set; 4 rows fused per traversal
def bsel(Ms, w, lv, pos, lw):
  if lv == 2:
    ((r0, r1), (r2, r3)) = Ms
    x = w >> pos
    return o4(r0, r1, r2, r3, 0 - (x & 1), 0 - ((x >> 1) & 1), 0 - ((x >> 2) & 1), 0 - ((x >> 3) & 1), lw)
  else:
    if lv < 2:
      return bsm(Ms, w, lv, pos, lw)
    else:
      (m1, m2) = Ms
      h = 1 << (lv - 1)
      return ort(bsel(m1, w, lv - 1, pos, lw), bsel(m2, w, lv - 1, pos + h, lw), lw)

def bsm(Ms, w, lv, pos, lw):
  switch lv:
    case 0:
      return rowm(Ms, 0 - ((w >> pos) & 1), lw)
    case _:
      (m1, m2) = Ms
      h = 1 << (lv-1)
      return ort(bsm(m1, w, lv-1, pos, lw), bsm(m2, w, lv-1, pos + h, lw), lw)

def gather(Ms, W, lv, lb, lw):
  if lv > lb:
    (m1, m2) = Ms
    (w1, w2) = W
    return ort(gather(m1, w1, lv - 1, lb, lw), gather(m2, w2, lv - 1, lb, lw), lw)
  else:
    if W == 0:
      return zt(lw, 0)
    else:
      return bsel(Ms, W, lv, 0, lw)

def sq(Mf, Mc, lv, l, lw, lb):
  switch lv:
    case 0:
      return gather(Mf, Mc, l, lb, lw)
    case _:
      (a, b) = Mc
      return (sq(Mf, a, lv-1, l, lw, lb), sq(Mf, b, lv-1, l, lw, lb))

# square until nothing changes (at most l + 1 squarings); the next squaring is spawned before the
# comparison decides (one round of lookahead)
def sqn(M, M2, l, lw, lb):
  M3 = sq(M2, M2, l, l, lw, lb)
  if neq(M, M2, l + lw):
    return sqn(M2, M3, l, lw, lb)
  else:
    return M2

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

def answer(qs, M, L, mk, lw):
  match qs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = qs.head
      w = get(M, (a << lw) | (b >> 4), L, mk)
      return List/Cons((w >> (b & 15)) & 1, answer(qs.tail, M, L, mk, lw))
