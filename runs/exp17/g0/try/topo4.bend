# t3_topo_order: n fixed steps (no convergence test). State: remaining in-degree per vertex (tuple tree; output
# vertices and padding are pushed to >= 2^20 so they never read as available). Each vertex's decrement row
# (1 at every out-neighbour, -2^20 at itself) is precomputed during the edge walk as a subtree of a tree of rows
# (keyed adds, collapse level by level). A step: leftmost available vertex a by a balanced reduce, then
# "take" row a out of the row tree (one O(log n) descent, no copying; each row is taken once), and subtract it
# leafwise from the state. Output = the steps' vertices in order.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (T, G) = walk(es, rows(l, l, 0), zt(l), l, m, l + l, top(l + l))
  return steps(T, pad(G, l, 0, n), l, m, n)

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

# row u = -2^20 (mod 2^24) at column u, 0 elsewhere
def rows(lv, l, base):
  switch lv:
    case 0:
      return row(l, 0, base)
    case _:
      h = 1 << (lv-1)
      return (rows(lv-1, l, base), rows(lv-1, l, base + h))

def row(lv, base, u):
  switch lv:
    case 0:
      return (base == u) * 15728640
    case _:
      h = 1 << (lv-1)
      return (row(lv-1, base, u), row(lv-1, base + h, u))

def pad(G, l, base, n):
  switch l:
    case 0:
      return G + (base >= n) * 1048576
    case _:
      (a, b) = G
      h = 1 << (l-1)
      return (pad(a, l-1, base, n), pad(b, l-1, base + h, n))

def add(t, k, l, m, v):
  switch l:
    case 0:
      return t + v
    case _:
      (a, b) = t
      if k & m:
        return (a, add(b, k, l-1, m >> 1, v))
      else:
        return (add(a, k, l-1, m >> 1, v), b)

def walk(es, T, G, l, m, L, M):
  match es:
    case List/Nil:
      return (T, G)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, add(T, (u << l) | v, L, M, 1), add(G, v, l, m, 1), l, m, L, M)

# (any available, index of the leftmost available)
def am(G, l, base):
  switch l:
    case 0:
      return (G == 0, base)
    case 1:
      (a, b) = G
      fa = a == 0
      fb = b == 0
      return (fa | fb, base + 1 - fa)
    case _:
      ((a, b), (c, d)) = G
      q = 1 << l
      h = q >> 1
      k = q >> 2
      (fa, ia) = am(a, l-2, base)
      (fb, ib) = am(b, l-2, base + k)
      (fc, ic) = am(c, l-2, base + h)
      (fd, id) = am(d, l-2, base + h + k)
      fab = fa | fb
      iab = ib + fa * (ia - ib)
      icd = id + fc * (ic - id)
      return (fab | fc | fd, icd + fab * (iab - icd))

def take(T, k, l, m):
  switch l:
    case 0:
      return (0, T)
    case 1:
      (a, b) = T
      if k & m:
        return ((a, 0), b)
      else:
        return ((0, b), a)
    case _:
      ((a, b), (c, d)) = T
      m2 = m >> 1
      m3 = m >> 2
      switch (((k & m) != 0) << 1) | ((k & m2) != 0):
        case 0:
          (a2, r) = take(a, k, l-2, m3)
          return (((a2, b), (c, d)), r)
        case 1:
          (b2, r) = take(b, k, l-2, m3)
          return (((a, b2), (c, d)), r)
        case 2:
          (c2, r) = take(c, k, l-2, m3)
          return (((a, b), (c2, d)), r)
        case _:
          (d2, r) = take(d, k, l-2, m3)
          return (((a, b), (c, d2)), r)

def sub(G, D, l):
  switch l:
    case 0:
      return G - D
    case 1:
      (g1, g2) = G
      (d1, d2) = D
      return (g1 - d1, g2 - d2)
    case _:
      ((g1, g2), (g3, g4)) = G
      ((d1, d2), (d3, d4)) = D
      return ((sub(g1, d1, l-2), sub(g2, d2, l-2)), (sub(g3, d3, l-2), sub(g4, d4, l-2)))

def steps(T, G, l, m, k):
  switch k:
    case 0:
      return []
    case _:
      (f, a) = am(G, l, 0)
      (T2, D) = take(T, a, l, m)
      return List/Cons(a, steps(T2, sub(G, D, l), l, m, k-1))
