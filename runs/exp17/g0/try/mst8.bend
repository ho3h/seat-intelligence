# t3_mst_second: Prim in n fixed steps (no convergence test), then ancestor rows by dataflow, then one pass
# over the edges. W = weight matrix as a tree of rows (keyed sets under the edge walk; INF = no edge); leaf v
# of the Prim state holds (key, parent, in-tree, row W[v]). A step is ONE traversal: the winner's row (which
# arrived with the previous reduce) is zipped down, every leaf relaxes, and the next winner is reduced on the
# way back up carrying its own row (no keyed descent anywhere in the loop). At the end every vertex holds
# its tree edge.
# Ancestor rows (after GRAPH-SWING-2): R_x[a] = max edge weight from x up to ancestor a, 0 at a = x, INF off
# x's root path; R_x = f(R_parent, w_x) is a pure dataflow: each vertex pushes a return-address sink at its
# parent's leaf and its row is computed from what arrives there (no rounds). Then the edge list (a second,
# concurrent walk of the input) fetches R_u, R_v per edge through sinks; maxpath(u, v) = min_a max(R_u[a], R_v[a])
# (the minimum sits at the LCA). Answer = MST + min over non-tree edges of w - maxpath (the second-best spanning
# tree is one swap away from an MST); INF when every edge is a tree edge.
def prog(x):
  (n, es) = x
  if n < 2:
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    L = l + l
    W = walk(es, zinf(L), l, L, top(L))
    (W1, R0) = take(W, 0, l, m)
    (mst, S) = steps(zip(init(l, 0, n), W1, l), R0, 0, l, n - 1)
    (RT, Q) = arows(S, l, 0, n, l, m, zl(l))
    (z1, PT) = dall(RT, Q, l)
    (Q2, cands) = ewalk(es, zl(l), l, m)
    z2 = dall2(PT, Q2, l)
    d = z1 + z2 + cands
    if d == 16777215:
      return 16777215
    else:
      return mst + d

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def top(L):
  switch L:
    case 0:
      return 0
    case _:
      return 1 << L-1

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def zinf(l):
  switch l:
    case 0:
      return 16777215
    case _:
      return (zinf(l-1), zinf(l-1))

def set(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, set(b, k, l-1, m >> 1, v))
      else:
        return (set(a, k, l-1, m >> 1, v), b)

def walk(es, W, l, L, M):
  match es:
    case List/Nil:
      return W
    case List/Cons:
      (u, v, w) = es.head
      return walk(es.tail, set(set(W, (u << l) | v, L, M, w), (v << l) | u, L, M, w), l, L, M)

def zip(S, W, l):
  switch l:
    case 0:
      (k, p, f) = S
      return (k, p, f, W)
    case _:
      (a, b) = S
      (c, d) = W
      return (zip(a, c, l-1), zip(b, d, l-1))

# leaf: (key, parent, in-tree); vertex 0 starts with key 0 (joins first, as its own parent)
def init(l, base, n):
  switch l:
    case 0:
      return ((base != 0) * 16777215, 0, (base == 0) | (base >= n))
    case _:
      h = 1 << (l-1)
      return (init(l-1, base, n), init(l-1, base + h, n))

def mn3(a, b):
  (wa, xa, pa) = a
  (wb, xb, pb) = b
  t = wb < wa
  return (wa + t * (wb - wa), xa + t * (xb - xa), pa + t * (pb - pa))

def am(S, l, base):
  switch l:
    case 0:
      (k, p, f, r) = S
      return (k | (f * 16777215), base, p)
    case _:
      (a, b) = S
      h = 1 << (l-1)
      return mn3(am(a, l-1, base), am(b, l-1, base + h))

def take(T, k, l, m):
  switch l:
    case 0:
      return (0, T)
    case _:
      (a, b) = T
      if k & m:
        (b2, r) = take(b, k, l-1, m >> 1)
        return ((a, b2), r)
      else:
        (a2, r) = take(a, k, l-1, m >> 1)
        return ((a2, b), r)

# The winner's row travels up with the reduce (after the "argmin-and-take" of GRAPH-SWING-2): every leaf offers
# (key, index, row, closer), where closer = lambda $keep: 0 and the leaf's next row is $keep; at each node the
# loser's closer is applied to the loser's own row (the row goes back to its leaf), only the winner travels on.
def rleaf(S, e, x, base):
  (k, p, f, r) = S
  t = (f == 0) & (e < k)
  k2 = k + t * (e - k)
  p2 = p + t * (x - p)
  f2 = f | (base == x)
  return ((k2, p2, f2, $keep), (k2 | (f2 * 16777215), base, r, lambda $keep: 0, 0))

def pk(a, b):
  (ka, ia, ra, ca, za) = a
  (kb, ib, rb, cb, zb) = b
  if kb < ka:
    return (kb, ib, rb, cb, za + zb + ca(ra))
  else:
    return (ka, ia, ra, ca, za + zb + cb(rb))

# relax every leaf with the winner row R (zipped down, no keyed descent) and reduce the next winner up
def relax(S, R, lv, base, x):
  switch lv:
    case 0:
      return rleaf(S, R, x, base)
    case _:
      (s1, s2) = S
      (r1, r2) = R
      h = 1 << (lv-1)
      (t1, c1) = relax(s1, r1, lv-1, base, x)
      (t2, c2) = relax(s2, r2, lv-1, base + h, x)
      return ((t1, t2), pk(c1, c2))

def getx(t, k, l, m):
  switch l:
    case 0:
      return (t, t)
    case _:
      (a, b) = t
      if k & m:
        (b2, v) = getx(b, k, l-1, m >> 1)
        return ((a, b2), v)
      else:
        (a2, v) = getx(a, k, l-1, m >> 1)
        return ((a2, b), v)

def mx(a, b):
  return a + (b > a) * (b - a)

def mn(a, b):
  return a + (b < a) * (b - a)

def steps(S, R, x, l, k):
  switch k:
    case 0:
      return (0, S)
    case _:
      (S2, c) = relax(S, R, l, 0, x)
      (w, x2, R2, cl, z) = c
      (tot, S3) = steps(S2, R2, x2, l, k-1)
      return (w + z + cl(0) + tot, S3)

type Br:
  Node { e, l, r }
  Leaf

def zl(l):
  switch l:
    case 0:
      return Br/Leaf
    case _:
      return (zl(l-1), zl(l-1))

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

# row of the root: 0 at itself, INF elsewhere
def urow(lv, base, x):
  switch lv:
    case 0:
      return (base != x) * 16777215
    case _:
      h = 1 << (lv-1)
      return (urow(lv-1, base, x), urow(lv-1, base + h, x))

def frow(r, lv, w, base, x):
  switch lv:
    case 0:
      return mx(r, w) * (base != x)
    case _:
      (a, b) = r
      h = 1 << (lv-1)
      return (frow(a, lv-1, w, base, x), frow(b, lv-1, w, base + h, x))

def pick(c, a, b):
  switch c:
    case 0:
      return b
    case _:
      return a

# leaf x: (row R_x, parent of x); every leaf pushes a sink at its parent's leaf (the root and padding
# leaves have parent 0 and ignore what arrives, so nothing waits on itself)
def arows(S, lv, base, n, l, m, Q):
  switch lv:
    case 0:
      (k, p, f, rw) = S
      r = pick((base == 0) | (base >= n), urow(l, 0, base), frow($rp, l, k, 0, base))
      Q2 = pushb(Q, p, l, m, lambda $rp: 0)
      return ((r, p), Q2)
    case _:
      (a, b) = S
      h = 1 << (lv-1)
      (ra, Q1) = arows(a, lv-1, base, n, l, m, Q)
      (rb, Q2) = arows(b, lv-1, base + h, n, l, m, Q1)
      return ((ra, rb), Q2)

# deliver every row to the sinks at its leaf; also returns the tree of (row, parent) for the edge pass
def dall(RT, Q, lv):
  switch lv:
    case 0:
      (r, p) = RT
      return (dl(r, Q), (r, p))
    case _:
      (r1, r2) = RT
      (q1, q2) = Q
      (z1, t1) = dall(r1, q1, lv-1)
      (z2, t2) = dall(r2, q2, lv-1)
      return (z1 + z2, (t1, t2))

def dl(v, t):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = t.e
      return f(v) + dl(v, t.l) + dl(v, t.r)

def dall2(PT, Q, lv):
  switch lv:
    case 0:
      return dl(PT, Q)
    case _:
      (r1, r2) = PT
      (q1, q2) = Q
      return dall2(r1, q1, lv-1) + dall2(r2, q2, lv-1)

def mm(a, b, lv):
  switch lv:
    case 0:
      return mx(a, b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return mn(mm(a1, b1, lv-1), mm(a2, b2, lv-1))

def cand(u, v, w, pu, pv, l):
  (ru, qu) = pu
  (rv, qv) = pv
  if (qu == v) | (qv == u):
    return 16777215
  else:
    return w - mm(ru, rv, l)

# second walk of the edge list: fetch (R_u, parent u) and (R_v, parent v) by return addresses
def ewalk(es, Q, l, m):
  match es:
    case List/Nil:
      return (Q, 16777215)
    case List/Cons:
      (u, v, w) = es.head
      Q2 = pushb(pushb(Q, u, l, m, lambda $pu: 0), v, l, m, lambda $pv: 0)
      (Q3, c) = ewalk(es.tail, Q2, l, m)
      return (Q3, mn(cand(u, v, w, $pu, $pv, l), c))
