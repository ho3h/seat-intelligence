# t3_bfs_order: level-synchronous BFS that computes every vertex's BFS position directly.
# pos(v) for a vertex first reached at level L+1 = (number of vertices at levels <= L) + rank of the key
# (min pos of its level-L neighbours, v) among the new vertices of level L+1 (this is exactly FIFO order
# with neighbours scanned in increasing id). Per level: the level-L frontier emits keyed min-updates of its
# positions into a fresh trie (vertex-keyed tuple tries, keys only in the control flow), new vertices build
# packed keys, and each new vertex counts smaller keys with a balanced reduction over the key trie (sum of
# level sizes squared, at most n^2 compares in all). Output: a block-threaded scatter of v into a
# position-keyed trie, flattened.
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
  (n, s, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zb(l), l, m)
  D0 = init(l, 0, s)
  (D, c) = levels(A, D0, 0, 1, 1, 1, l, m)
  O = scat(D, l, 0, l, m)
  return flat(O, l, 0, c, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, pushb(pushb(A, u, l, m, v), v, l, m, u), l, m)

def init(l, base, s):
  switch l:
    case 0:
      if base == s:
        return (0, 0)
      else:
        return (16777215, 0)
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, s), init(l-1, base + h, s))

def eb(t, p, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      return eb(t.r, p, eb(t.l, p, updmin(N, t.e, l, m, p), l, m), l, m)

def emit(A, D, L, l, lv, m, N):
  switch lv:
    case 0:
      (d, p) = D
      q = d == L
      return eb(A, p * q + (1 - q) * 16777215, N, l, m)
    case _:
      (a1, a2) = A
      (d1, d2) = D
      return emit(a2, d2, L, l, lv-1, m, emit(a1, d1, L, l, lv-1, m, N))

# key trie: (N << l) | v for vertices first reached now, INF otherwise; also their number
def keys(D, N, lv, idx, l):
  switch lv:
    case 0:
      (d, p) = D
      nw = (d == 16777215) & (N < 16777215)
      if nw:
        return ((N << l) | idx, 1)
      else:
        return (16777215, 0)
    case _:
      (d1, d2) = D
      (n1, n2) = N
      h = 1 << (lv-1)
      (k1, c1) = keys(d1, n1, lv-1, idx, l)
      (k2, c2) = keys(d2, n2, lv-1, idx + h, l)
      return ((k1, k2), c1 + c2)

def cntl(K, k, lv):
  switch lv:
    case 0:
      return K < k
    case _:
      (a, b) = K
      return cntl(a, k, lv-1) + cntl(b, k, lv-1)

def upd(D, K, Ka, lv, L1, base, l):
  switch lv:
    case 0:
      if K == 16777215:
        return D
      else:
        return (L1, base + cntl(Ka, K, l))
    case _:
      (d1, d2) = D
      (k1, k2) = K
      return (upd(d1, k1, Ka, lv-1, L1, base, l), upd(d2, k2, Ka, lv-1, L1, base, l))

# lagged: level L+1 is started when level L-2 found new vertices (spare levels find none and are cheap)
def levels(A, D, L, base, c1, c2, l, m):
  N = emit(A, D, L, l, l, m, zt(l, 16777215))
  (K, c) = keys(D, N, l, 0, l)
  D2 = upd(D, K, K, l, L + 1, base, l)
  if c2:
    return levels(A, D2, L + 1, base + c, c, c1, l, m)
  else:
    return (D2, base + c)

def addt(a, b, l):
  switch l:
    case 0:
      return a + b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (addt(a1, b1, l-1), addt(a2, b2, l-1))

def addk(t, k, l, m, x):
  switch l:
    case 0:
      return t + x
    case _:
      (a, b) = t
      if k & m:
        return (a, addk(b, k, l-1, m >> 1, x))
      else:
        return (addk(a, k, l-1, m >> 1, x), b)

# O[pos(v)] = v + 1 for visited v; blocks of 8 vertices thread privately, blocks are added pointwise
def scatt(D, lv, base, l, m, C):
  switch lv:
    case 0:
      (d, p) = D
      vis = d != 16777215
      return addk(C, p, l, m, vis * (base + 1))
    case _:
      (a, b) = D
      h = 1 << (lv-1)
      return scatt(b, lv-1, base + h, l, m, scatt(a, lv-1, base, l, m, C))

def scat(D, lv, base, l, m):
  if lv <= 3:
    return scatt(D, lv, base, l, m, zt(l, 0))
  else:
    (a, b) = D
    h = 1 << (lv - 1)
    return addt(scat(a, lv - 1, base, l, m), scat(b, lv - 1, base + h, l, m), l)

def flat(t, l, base, c, acc):
  switch l:
    case 0:
      if base < c:
        return List/Cons(t - 1, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, c, flat(b, l-1, base + h, c, acc))
