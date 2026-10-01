# t3_wsp_dist: frontier Bellman-Ford over vertex-keyed tuple tries (the wsp_all_from engine, undirected).
# A: adjacency, leaf u = Braun tree of (v, w). D: leaf v = (dist, improved flag). Each round every improved
# leaf emits keyed min-updates (v, d + w) into a fresh candidate trie (their switches depend only on keys, so
# they collapse level by level); merge leafwise and OR-reduce; the next round's emission is spawned before the
# OR-reduce decides. Answer: D[t].
#include base
def prog(x):
  (n, s, t, es) = x
  if (s >= n) | (t >= n):
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    A = walk(es, zb(l), l, m)
    D0 = init(l, 0, s)
    D = loop(A, D0, emit(A, D0, l, l, m, zt(l, 16777215)), l, m)
    (d, f) = get(D, t, l, m)
    return d

def init(l, base, s):
  switch l:
    case 0:
      if base == s:
        return (0, 1)
      else:
        return (16777215, 0)
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, s), init(l-1, base + h, s))

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v, w) = es.head
      return walk(es.tail, pushb(pushb(A, u, l, m, (v, w)), v, l, m, (u, w)), l, m)

def eb(t, d, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      (v, w) = t.e
      return eb(t.r, d, eb(t.l, d, updmin(N, v, l, m, d + w), l, m), l, m)

def emit(A, D, l, lv, m, N):
  switch lv:
    case 0:
      (d, f) = D
      if f:
        return eb(A, d, N, l, m)
      else:
        return N
    case _:
      (a1, a2) = A
      (d1, d2) = D
      return emit(a2, d2, l, lv-1, m, emit(a1, d1, l, lv-1, m, N))

def merge(D, N, lv):
  switch lv:
    case 0:
      (d, f) = D
      t = N < d
      return ((d - t * (d - N), t), t)
    case _:
      (d1, d2) = D
      (n1, n2) = N
      (x1, a1) = merge(d1, n1, lv-1)
      (x2, a2) = merge(d2, n2, lv-1)
      return ((x1, x2), a1 | a2)

def loop(A, D, N, l, m):
  (D2, any) = merge(D, N, l)
  N2 = emit(A, D2, l, l, m, zt(l, 16777215))
  if any:
    return loop(A, D2, N2, l, m)
  else:
    return D2
