# t3_msf_weight: Boruvka. Edges live in a Braun tree (one list walk, each edge gets its index), so every
# phase is a parallel pass over the tree, not a list walk. Edge order: (w, index), packed (w << s) | index.
# Per phase (at most log2 n + 1 phases):
#  1. every edge reads its endpoints' component labels (keyed lookups) and offers (pack, other component) to
#     both components: keyed min-updates threaded through small subtrees (height <= 3) of the edge tree, and
#     the per-subtree component tries merged pointwise up the tree (no long update thread);
#  2. each component's hook = the other side of its min edge; a mutual pair keeps the smaller id as root and
#     its shared edge is counted once;
#  3. pointer jumping P <- P o P until it stops changing, then relabel every vertex.
#include base
def prog(x):
  (n, es) = x
  (l, mk) = lvl(n, 0, 1)
  (E, c) = walk(es, Br/Leaf, 0)
  (s, sm) = lvl(c, 0, 1)
  (H, hm) = lvl(c + 1, 0, 1)
  return phases(E, ids(l, 0), 0, l, mk, s, H)

def ids(l, base):
  switch l:
    case 0:
      return base
    case _:
      h = 1 << (l-1)
      return (ids(l-1, base), ids(l-1, base + h))

def walk(es, E, c):
  match es:
    case List/Nil:
      return (E, c)
    case List/Cons:
      (u, v, w) = es.head
      return walk(es.tail, bins(E, (u, v, w, c)), c + 1)

def umin(t, k, l, m, p, o):
  switch l:
    case 0:
      (p0, o0) = t
      b = p < p0
      return (p0 - b * (p0 - p), o0 + b * (o - o0))
    case _:
      (a, c) = t
      if k & m:
        return (a, umin(c, k, l-1, m >> 1, p, o))
      else:
        return (umin(a, k, l-1, m >> 1, p, o), c)

def mrg(a, b, l):
  switch l:
    case 0:
      (p0, o0) = a
      (p1, o1) = b
      t = p1 < p0
      return (p0 - t * (p0 - p1), o0 + t * (o1 - o0))
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (mrg(a1, b1, l-1), mrg(a2, b2, l-1))

def offer(M, e, L, l, mk, s):
  (u, v, w, i) = e
  lu = get(L, u, l, mk)
  lv = get(L, v, l, mk)
  d = lu != lv
  pk = (w << s) | i
  pe = pk + (1 - d) * (16777215 - pk)
  return umin(umin(M, lu, l, mk, pe, lv), lv, l, mk, pe, lu)

def thr(t, L, M, l, mk, s):
  match t:
    case Br/Leaf:
      return M
    case Br/Node:
      return thr(t.r, L, thr(t.l, L, offer(M, t.e, L, l, mk, s), l, mk, s), l, mk, s)

def minE(t, L, h, l, mk, s):
  if h <= 3:
    return thr(t, L, zt(l, (16777215, 0)), l, mk, s)
  else:
    match t:
      case Br/Leaf:
        return zt(l, (16777215, 0))
      case Br/Node:
        M = mrg(minE(t.l, L, h - 1, l, mk, s), minE(t.r, L, h - 1, l, mk, s), l)
        return offer(M, t.e, L, l, mk, s)

# P0[c] = other side of c's min edge (c itself if none); any = some component has an edge out
def hooks(M, lv, c):
  switch lv:
    case 0:
      (p, o) = M
      v = p != 16777215
      return (c + v * (o - c), v)
    case _:
      (m1, m2) = M
      h = 1 << (lv-1)
      (a1, v1) = hooks(m1, lv-1, c)
      (a2, v2) = hooks(m2, lv-1, c + h)
      return ((a1, a2), v1 | v2)

# break mutual pairs (smaller id becomes the root) and sum the weights of the chosen edges, once each
def brk(M, P, Pa, lv, c, l, mk, s):
  switch lv:
    case 0:
      (p, o) = M
      v = p != 16777215
      r = v & (get(Pa, o, l, mk) == c) & (c < o)
      return (P + r * (c - P), (v - r) * (p >> s))
    case _:
      (m1, m2) = M
      (q1, q2) = P
      h = 1 << (lv-1)
      (a1, w1) = brk(m1, q1, Pa, lv-1, c, l, mk, s)
      (a2, w2) = brk(m2, q2, Pa, lv-1, c + h, l, mk, s)
      return ((a1, a2), w1 + w2)

def comp(P, Pa, lv, l, mk):
  switch lv:
    case 0:
      return get(Pa, P, l, mk)
    case _:
      (a, b) = P
      return (comp(a, Pa, lv-1, l, mk), comp(b, Pa, lv-1, l, mk))

# pointer jumping until nothing changes (hook trees are usually shallow)
def jump(P, k, l, mk):
  P2 = comp(P, P, l, l, mk)
  if neq(P, P2, l):
    return jump(P2, k, l, mk)
  else:
    return P2

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

def phases(E, L, acc, l, mk, s, H):
  M = minE(E, L, H, l, mk, s)
  (P0, any) = hooks(M, l, 0)
  if any:
    (P1, ws) = brk(M, P0, P0, l, 0, l, mk, s)
    P = jump(P1, l, l, mk)
    return phases(E, comp(L, P, l, l, mk), acc + ws, l, mk, s, H)
  else:
    return acc
