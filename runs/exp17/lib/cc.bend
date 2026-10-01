# ---- cc: frontier min-label propagation over vertex-keyed tuple-trees (exp7 engine).
# A: adjacency, leaf u = Braun tree of neighbours. D: leaf v = (label, improved-last-round flag).
# Each round every improved leaf emits keyed min-updates into a fresh candidate tree (threaded), then D and
# the candidates merge leafwise with an OR-reduce; the next round's emission is spawned before the OR decides.
type Br:
  Node { e, l, r }
  Leaf

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

def walk_und(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk_und(es.tail, pushb(pushb(A, u, l, m, v), v, l, m, u), l, m)

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

def loop(A, D, N, l, m):
  (D2, any) = merge(D, N, l)
  N2 = emit(A, D2, l, l, m, zinf(l))
  if any:
    return loop(A, D2, N2, l, m)
  else:
    return D2

# initial labels: own id (min-label) for real vertices, inf for padding
def init_min(l, base, n):
  switch l:
    case 0:
      if base < n:
        return (base, 1)
      else:
        return (16777215, 0)
    case _:
      h = 1 << (l-1)
      return (init_min(l-1, base, n), init_min(l-1, base + h, n))

# initial labels for max-label (canonical = largest member): K - id, so min over it is max over ids
def init_max(l, base, n, K):
  switch l:
    case 0:
      if base < n:
        return (K - base, 1)
      else:
        return (16777215, 0)
    case _:
      h = 1 << (l-1)
      return (init_max(l-1, base, n, K), init_max(l-1, base + h, n, K))

def cc_min(n, es):
  (l, m) = lvl(n, 0, 1)
  A = walk_und(es, zb(l), l, m)
  D0 = init_min(l, 0, n)
  return (loop(A, D0, emit(A, D0, l, l, m, zinf(l)), l, m), l, m)
