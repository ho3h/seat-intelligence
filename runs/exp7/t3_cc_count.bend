# t3_cc_count: frontier min-label propagation (the wsp_all_from engine with labels instead of distances).
# Every vertex starts with its own id as label and in the frontier; improved labels are pushed to neighbours
# with keyed min-updates; at the fixpoint the answer is the number of vertices whose label is their own id.
# A: out-adjacency, leaf u = Braun tree of (v, w) (balanced, so a leaf's emission is O(log deg) deep).
# D: leaf v = (dist, improved-last-round flag). Each round: every improved leaf emits keyed min-updates
# (v, d + w) into a fresh candidate tree N (threaded through the traversal; the updates' switches depend
# only on keys, so they collapse level by level); merge D with N leafwise and OR-reduce the flags;
# repeat while anything improved.
# (Node first: a nullary Leaf with tag 0 would be merged with List/Nil by the compiler)
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zb(l), l, m)
  D0 = init(l, 0, n)
  D = loop(A, D0, emit(A, D0, l, l, m, zinf(l)), l, m)
  return roots(D, l, 0, n)

def roots(t, l, base, n):
  switch l:
    case 0:
      (d, f) = t
      return (d == base) & (base < n)
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return roots(a, l-1, base, n) + roots(b, l-1, base + h, n)

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

def zinf(l):
  switch l:
    case 0:
      return 16777215
    case _:
      return (zinf(l-1), zinf(l-1))

def init(l, base, n):
  switch l:
    case 0:
      if base < n:
        return (base, 1)
      else:
        return (16777215, 0)
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, n), init(l-1, base + h, n))

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
      return walk(es.tail, pushb(pushb(A, u, l, m, v), v, l, m, u), l, m)

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

def eb(t, d, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      return eb(t.r, d, eb(t.l, d, updmin(N, t.e, l, m, d), l, m), l, m)

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

# N is the emission of D, spawned one round ahead: the next round's emission starts from D2's leaf
# flags without waiting for the OR-reduce (a final, empty emission is wasted work).
def loop(A, D, N, l, m):
  (D2, any) = merge(D, N, l)
  N2 = emit(A, D2, l, l, m, zinf(l))
  if any:
    return loop(A, D2, N2, l, m)
  else:
    return D2
