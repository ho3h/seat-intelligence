# t3_max_flow: Edmonds-Karp with cheap exits (s == t or out of range answer 0 without reading the list).
# Residual arcs live in per-vertex Braun trees (arc id, head, residual cap) inside a vertex-keyed tuple
# trie (forward arc 2i, reverse 2i+1). BFS from s is frontier rounds of keyed min-updates carrying (parent
# arc, bottleneck); after t is reached the path is traced back with keyed reads and the residual caps on it
# are changed by keyed updates (each maps one vertex's Braun tree).
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
  (n, s, t, es) = x
  if (s == t) | (s >= n) | (t >= n):
    return 0
  else:
    (l, m) = lvl(n, 0, 1)
    A = walk(es, zb(l), 0, l, m)
    return phase(A, s, t, 0, l, m)

def walk(es, A, i, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v, w) = es.head
      return walk(es.tail, pushb(pushb(A, u, l, m, (i << 1, v, w)), v, l, m, ((i << 1) | 1, u, 0)), i + 1, l, m)

def init(l, base, s):
  switch l:
    case 0:
      if base == s:
        return (0, 0, 0, 16777215)
      else:
        return (16777215, 0, 0, 0)
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, s), init(l-1, base + h, s))

# candidate leaf: (parent vertex, arc id, bottleneck); smallest parent id wins
def umin(t, k, l, m, u, a, b):
  switch l:
    case 0:
      (p0, a0, b0) = t
      c = u < p0
      return (p0 - c * (p0 - u), a0 + c * (a - a0), b0 + c * (b - b0))
    case _:
      (x, y) = t
      if k & m:
        return (x, umin(y, k, l-1, m >> 1, u, a, b))
      else:
        return (umin(x, k, l-1, m >> 1, u, a, b), y)

def mn(a, b):
  return a - (a > b) * (a - b)

def eb(t, u, bn, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      (id, v, c) = t.e
      N1 = eb(t.l, u, bn, N, l, m)
      if c:
        return eb(t.r, u, bn, umin(N1, v, l, m, u, id, mn(bn, c)), l, m)
      else:
        return eb(t.r, u, bn, N1, l, m)

def emit(A, S, k, l, lv, m, N, u):
  switch lv:
    case 0:
      (d, pu, pa, bn) = S
      if d == k:
        return eb(A, u, bn, N, l, m)
      else:
        return N
    case _:
      (a1, a2) = A
      (s1, s2) = S
      h = 1 << (lv-1)
      return emit(a2, s2, k, l, lv-1, m, emit(a1, s1, k, l, lv-1, m, N, u), u + h)

# merge candidates: newly reached vertices get layer k1; flags: any new, t reached
def merge(S, N, k1, lv, v, t):
  switch lv:
    case 0:
      (d, pu, pa, bn) = S
      (p, a, b) = N
      nw = (d == 16777215) & (p != 16777215)
      if nw:
        return ((k1, p, a, b), 1, v == t)
      else:
        return (S, 0, 0)
    case _:
      (s1, s2) = S
      (n1, n2) = N
      h = 1 << (lv-1)
      (x1, a1, t1) = merge(s1, n1, k1, lv-1, v, t)
      (x2, a2, t2) = merge(s2, n2, k1, lv-1, v + h, t)
      return ((x1, x2), a1 | a2, t1 | t2)

def bfs(A, S, k, t, l, m):
  N = emit(A, S, k, l, l, m, zt(l, (16777215, 0, 0)), 0)
  (S2, any, hit) = merge(S, N, k + 1, l, 0, t)
  if hit:
    return (1, S2)
  else:
    if any:
      return bfs(A, S2, k + 1, t, l, m)
    else:
      return (0, S2)

def bmap(t, id, ad, sb):
  match t:
    case Br/Leaf:
      return Br/Leaf
    case Br/Node:
      (i, v, c) = t.e
      e = i == id
      return Br/Node((i, v, c + e * ad - e * sb), bmap(t.l, id, ad, sb), bmap(t.r, id, ad, sb))

def updc(A, k, l, m, id, ad, sb):
  switch l:
    case 0:
      return bmap(A, id, ad, sb)
    case _:
      (a, b) = A
      if k & m:
        return (a, updc(b, k, l-1, m >> 1, id, ad, sb))
      else:
        return (updc(a, k, l-1, m >> 1, id, ad, sb), b)

def trace(S, v, s, A, f, l, m):
  if v == s:
    return A
  else:
    (d, pu, pa, bn) = get(S, v, l, m)
    A2 = updc(updc(A, pu, l, m, pa, 0, f), v, l, m, pa ^ 1, f, 0)
    return trace(S, pu, s, A2, f, l, m)

def phase(A, s, t, flow, l, m):
  (found, S) = bfs(A, init(l, 0, s), 0, t, l, m)
  if found:
    (d, pu, pa, f) = get(S, t, l, m)
    return phase(trace(S, t, s, A, f, l, m), s, t, flow + f, l, m)
  else:
    return flow
