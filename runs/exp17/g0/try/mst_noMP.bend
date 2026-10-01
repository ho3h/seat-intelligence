# t3_mst_second: Prim in n fixed steps (no convergence test) plus path-maximum rows.
# W = weight matrix as a tree of rows (keyed sets under the edge walk; INF = no edge), kept twice: one copy
# feeds Prim (row x is "taken" out when x joins: one descent, no copying), the other loses its tree edges
# and is compared at the end. Prim state per vertex: (key, parent, in-tree). A step: argmin by a balanced
# reduce -> (w, x, p); take row x; update keys leafwise. Path maxima MP (symmetric over tree vertices):
# when x joins via (p, w): every row y gets MP[y][x] = max(MP[y][p], w) (one read + one write per row, in
# parallel), and row x = max(copy of row p, w) with MP[x][x] = 0. These updates hang off Prim's steps and
# pipeline behind them. Answer = MST + min over non-tree edges (u, v, w) of w - MP[u][v] (the second-best
# spanning tree differs from an MST by one swap); INF if every edge is a tree edge.
def prog(x):
  (n, es) = x
  if n < 2:
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    L = l + l
    W = walk(es, zinf(L), l, L, top(L))
    S0 = init(l, 0, n)
    (mst, W2, MP) = steps(W, W, S0, zt(L), l, m, n)
    d = fin(W2, MP, L)
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

# leaf: (key, parent, in-tree); vertex 0 starts with key 0 (joins first, as its own parent)
def init(l, base, n):
  switch l:
    case 0:
      return ((base != 0) * 16777215, 0, base >= n)
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
      (k, p, f) = S
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

def relax(S, R, l, base, x):
  switch l:
    case 0:
      (k, p, f) = S
      t = (f == 0) & (R < k)
      return (k + t * (R - k), p + t * (x - p), f | (base == x))
    case _:
      (s1, s2) = S
      (r1, r2) = R
      h = 1 << (l-1)
      return (relax(s1, r1, l-1, base, x), relax(s2, r2, l-1, base + h, x))

def mx(a, b):
  return a + (b > a) * (b - a)

# returns (row, row[k]) without copying the row
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

# every row y: MP[y][x] = max(MP[y][p], w)
def rowsupd(MP, lv, l, m, x, p, w):
  switch lv:
    case 0:
      (r, v) = getx(MP, p, l, m)
      return set(r, x, l, m, mx(v, w))
    case _:
      (a, b) = MP
      return (rowsupd(a, lv-1, l, m, x, p, w), rowsupd(b, lv-1, l, m, x, p, w))

# (MP, copy of row p)
def getrow(t, k, l, m):
  switch l:
    case 0:
      return (t, t)
    case _:
      (a, b) = t
      if k & m:
        (b2, r) = getrow(b, k, l-1, m >> 1)
        return ((a, b2), r)
      else:
        (a2, r) = getrow(a, k, l-1, m >> 1)
        return ((a2, b), r)

def rmax(r, lv, w, base, x):
  switch lv:
    case 0:
      return mx(r, w) * (base != x)
    case _:
      (a, b) = r
      h = 1 << (lv-1)
      return (rmax(a, lv-1, w, base, x), rmax(b, lv-1, w, base + h, x))

def steps(W, W2, S, MP, l, m, k):
  switch k:
    case 0:
      return (0, W2, MP)
    case _:
      (w, x, p) = am(S, l, 0)
      (Wt, R) = take(W, x, l, m)
      S2 = relax(S, R, l, 0, x)
      L = l + l
      M = top(L)
      W3 = set(set(W2, (x << l) | p, L, M, 16777215), (p << l) | x, L, M, 16777215)
      MP2 = MP
      (tot, W4, MP3) = steps(Wt, W3, S2, MP2, l, m, k-1)
      return (w + tot, W4, MP3)

def mn(a, b):
  return a + (b < a) * (b - a)

def fin(W, MP, L):
  switch L:
    case 0:
      if W == 16777215:
        return 16777215
      else:
        return W - MP
    case _:
      (w1, w2) = W
      (m1, m2) = MP
      return mn(fin(w1, m1, L-1), fin(w2, m2, L-1))
