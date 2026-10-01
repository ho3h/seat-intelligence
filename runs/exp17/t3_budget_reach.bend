# t3_budget_reach: the wsp_all_from engine (frontier Bellman-Ford over vertex-keyed tuple-trees), undirected,
# with the budget as an acceptance bound (a candidate joins only if it is <= b), then a balanced count.
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
  (n, s, bud, es) = x
  if s >= n:
    return 0
  else:
    (l, m) = lvl(n, 0, 1)
    A = walk(es, zb(l), l, m)
    D0 = init(l, 0, s)
    D = loop(A, D0, emit(A, D0, l, l, m, zinf(l)), l, m, bud)
    return cntb(D, l, bud)

def cntb(t, l, bud):
  switch l:
    case 0:
      (d, f) = t
      return (d < 16777215) & (d <= bud)
    case _:
      (a, b) = t
      return cntb(a, l-1, bud) + cntb(b, l-1, bud)

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
      (u, v, w) = es.head
      return walk(es.tail, pushb(pushb(A, u, l, m, (v, w)), v, l, m, (u, w)), l, m)

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

def merge(D, N, lv, bud):
  switch lv:
    case 0:
      (d, f) = D
      t = (N < d) & (N <= bud)
      return ((d - t * (d - N), t), t)
    case _:
      (d1, d2) = D
      (n1, n2) = N
      (x1, a1) = merge(d1, n1, lv-1, bud)
      (x2, a2) = merge(d2, n2, lv-1, bud)
      return ((x1, x2), a1 | a2)

# N is the emission of D, spawned one round ahead: the next round's emission starts from D2's leaf
# flags without waiting for the OR-reduce (a final, empty emission is wasted work).
def loop(A, D, N, l, m, bud):
  (D2, any) = merge(D, N, l, bud)
  N2 = emit(A, D2, l, l, m, zinf(l))
  if any:
    return loop(A, D2, N2, l, m, bud)
  else:
    return D2
