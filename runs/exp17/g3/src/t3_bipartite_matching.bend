# t3_bipartite_matching: phases of multi-source alternating BFS with simultaneous augmentation along
# vertex-disjoint shortest paths (one per BFS tree). Per phase: every free left vertex is a root; a layer
# of left vertices emits keyed min-updates (parent, root) to its right neighbours (vertex-keyed tuple
# tries, ungated emission: non-frontier vertices offer INF); new right vertices either are free (stop: augment) or pass the search to
# their mate. Each tree that reached a free right vertex augments along the path to its smallest such
# vertex: backward steps are data-keyed scatters (blocks of 8 threaded, blocks added pointwise). The first
# phase is a parallel greedy matching; typically only a few more phases are needed.
#include base
#include scatkv
def prog(x):
  (a, b, es) = x
  (l, m) = lvl(a + (b > a) * (b - a), 0, 1)
  A = walk(es, zb(l), l, m)
  I = zt(l, 16777215)
  return phase(A, I, I, a, 0, l, m)

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, pushb(A, u, l, m, v), l, m)

# left state: (dist, root); free real left vertices are roots at dist 0
def lroots(ML, lv, u, a):
  switch lv:
    case 0:
      if (u < a) & (ML == 16777215):
        return (0, u)
      else:
        return (16777215, 0)
    case _:
      (m1, m2) = ML
      h = 1 << (lv-1)
      return (lroots(m1, lv-1, u, a), lroots(m2, lv-1, u + h, a))

def umin(t, k, l, m, p, o):
  switch l:
    case 0:
      (p0, o0) = t
      c = p < p0
      return (p0 - c * (p0 - p), o0 + c * (o - o0))
    case _:
      (x, y) = t
      if k & m:
        return (x, umin(y, k, l-1, m >> 1, p, o))
      else:
        return (umin(x, k, l-1, m >> 1, p, o), y)

def eb(t, u, r, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      return eb(t.r, u, r, eb(t.l, u, r, umin(N, t.e, l, m, u, r), l, m), l, m)

def emit(A, LS, k, l, lv, m, N, u):
  switch lv:
    case 0:
      (d, r) = LS
      q = d == k
      return eb(A, u * q + (1 - q) * 16777215, r, N, l, m)
    case _:
      (a1, a2) = A
      (s1, s2) = LS
      h = 1 << (lv-1)
      return emit(a2, s2, k, l, lv-1, m, emit(a1, s1, k, l, lv-1, m, N, u), u + h)

# right state (dist, parent, root) updated by candidates N; also (key, x) leaves for the next left layer
# (mate <- root + 1), and flags any-new / any-new-free
def rstep(RS, N, MR, k, lv):
  switch lv:
    case 0:
      (d, p, r) = RS
      (np, nr) = N
      nw = (d == 16777215) & (np != 16777215)
      fr = nw & (MR == 16777215)
      if nw:
        return ((k, np, nr), (MR * (1 - fr), (1 - fr) * (nr + 1)), nw, fr)
      else:
        return (RS, (0, 0), 0, 0)
    case _:
      (s1, s2) = RS
      (n1, n2) = N
      (q1, q2) = MR
      (x1, y1, a1, f1) = rstep(s1, n1, q1, k, lv-1)
      (x2, y2, a2, f2) = rstep(s2, n2, q2, k, lv-1)
      return ((x1, x2), (y1, y2), a1 | a2, f1 | f2)

def lnext(LS, H, k1, lv):
  switch lv:
    case 0:
      if H:
        return (k1, H - 1)
      else:
        return LS
    case _:
      (s1, s2) = LS
      (h1, h2) = H
      return (lnext(s1, h1, k1, lv-1), lnext(s2, h2, k1, lv-1))

def bfs(A, LS, RS, ML, MR, k, l, m):
  N = emit(A, LS, k, l, l, m, zt(l, (16777215, 0)), 0)
  (RS2, KV, anew, afree) = rstep(RS, N, MR, k, l)
  if afree:
    return (1, RS2, k)
  else:
    if anew:
      H = scatkv(KV, l, l, m)
      return bfs(A, lnext(LS, H, k + 1, l), RS2, ML, MR, k + 1, l, m)
    else:
      return (0, RS2, k)

# endpoints (new free right vertices at layer k): offer v + 1 to their root, keep the min per root
def ends(RS, MR, k, lv, v):
  switch lv:
    case 0:
      (d, p, r) = RS
      e = (d == k) & (MR == 16777215)
      return (r, e * (v + 1))
    case _:
      (s1, s2) = RS
      (q1, q2) = MR
      h = 1 << (lv-1)
      return (ends(s1, q1, k, lv-1, v), ends(s2, q2, k, lv-1, v + h))

def umn(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, umn(b, k, l-1, m >> 1, x))
      else:
        return (umn(a, k, l-1, m >> 1, x), b)

def mint(a, b, l):
  switch l:
    case 0:
      return a - (a > b) * (a - b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (mint(a1, b1, l-1), mint(a2, b2, l-1))

def smnt(KV, lv, l, m, C):
  switch lv:
    case 0:
      (k, x) = KV
      return umn(C, k, l, m, x + (x == 0) * 16777215)
    case _:
      (a, b) = KV
      return smnt(b, lv-1, l, m, smnt(a, lv-1, l, m, C))

def scatmin(KV, lv, l, m):
  if lv <= 3:
    return smnt(KV, lv, l, m, zt(l, 16777215))
  else:
    (a, b) = KV
    return mint(scatmin(a, lv - 1, l, m), scatmin(b, lv - 1, l, m), l)

# selected endpoints: v whose root's min endpoint is v; returns flag trie and count
def sel(KV, C, lv, l, m):
  switch lv:
    case 0:
      (r, x) = KV
      s = (x != 0) & (get(C, r, l, m) == x)
      return (s, s)
    case _:
      (k1, k2) = KV
      (s1, c1) = sel(k1, C, lv-1, l, m)
      (s2, c2) = sel(k2, C, lv-1, l, m)
      return ((s1, s2), c1 + c2)

# backward step: selected right v gets mate parent(v); left hits H[u] = v + 1
def bstep(S, RS, MR, lv, v):
  switch lv:
    case 0:
      (d, p, r) = RS
      if S:
        return (p, (p, v + 1))
      else:
        return (MR, (0, 0))
    case _:
      (s1, s2) = S
      (r1, r2) = RS
      (q1, q2) = MR
      h = 1 << (lv-1)
      (a1, k1) = bstep(s1, r1, q1, lv-1, v)
      (a2, k2) = bstep(s2, r2, q2, lv-1, v + h)
      return ((a1, a2), (k1, k2))

# left side of a step: hit u takes mate H - 1; its old mate (if any) is selected next
def lstep(H, ML, lv):
  switch lv:
    case 0:
      if H:
        g = ML != 16777215
        return (H - 1, (ML * g, g), g)
      else:
        return (ML, (0, 0), 0)
    case _:
      (h1, h2) = H
      (q1, q2) = ML
      (a1, k1, g1) = lstep(h1, q1, lv-1)
      (a2, k2, g2) = lstep(h2, q2, lv-1)
      return ((a1, a2), (k1, k2), g1 | g2)

def aug(S, RS, ML, MR, l, m):
  (MR2, KV) = bstep(S, RS, MR, l, 0)
  H = scatkv(KV, l, l, m)
  (ML2, KV2, more) = lstep(H, ML, l)
  if more:
    return aug(scatkv(KV2, l, l, m), RS, ML2, MR2, l, m)
  else:
    return (ML2, MR2)

def phase(A, ML, MR, a, size, l, m):
  LS = lroots(ML, l, 0, a)
  RS0 = zt(l, (16777215, 0, 0))
  (found, RS, k) = bfs(A, LS, RS0, ML, MR, 0, l, m)
  if found:
    E = ends(RS, MR, k, l, 0)
    C = scatmin(E, l, l, m)
    (S, c) = sel(E, C, l, l, m)
    (ML2, MR2) = aug(S, RS, ML, MR, l, m)
    return phase(A, ML2, MR2, a, size + c, l, m)
  else:
    return size
