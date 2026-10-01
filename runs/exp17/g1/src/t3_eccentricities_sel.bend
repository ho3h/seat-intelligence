# t3_eccentricities: all-sources BFS as bitset rounds (msbfs idea). Rows are word trees (16-bit words); A is the
# adjacency bit matrix (ONE tuple tree: l vertex levels then lw word levels), built by keyed ORs in one walk.
# R_v = ball around v; a round sets R'_v = R_v | OR_{u in A_v} R_u by a divide-and-conquer traversal of v's
# adjacency row alongside R (bits select rows, rows OR leafwise); every vertex runs this in parallel.
# ecc(v) = number of rounds in which R_v was not yet full; stop when every ball is full (the next round is
# spawned before the fullness test decides: one-round lookahead).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  kb = l - lw
  L = l + lw
  (xx, M) = lvl(1 << L, 0, 1)
  A = walk(es, zt(L), lw, L, M)
  R0 = ident(l, 0, lw, n)
  F = full(lw, 0, n)
  E = loop(A, R0, zt(l), F, l, lw, kb, n)
  return flat(E, l, 0, n, [])

def walk(es, C, lw, L, M):
  match es:
    case List/Nil:
      return C
    case List/Cons:
      (u, v) = es.head
      C1 = ork(C, (u << lw) | (v >> 4), L, M, 1 << (v & 15))
      return walk(es.tail, ork(C1, (v << lw) | (u >> 4), L, M, 1 << (u & 15)), lw, L, M)

def ident(lv, base, lw, n):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return ork(zt(lw), base >> 4, lw, mw, (base < n) << (base & 15))
    case _:
      h = 1 << (lv-1)
      return (ident(lv-1, base, lw, n), ident(lv-1, base + h, lw, n))

# row with the bits of vertices < n set (word base = first vertex of the word)
def full(lw, base, n):
  switch lw:
    case 0:
      k = n - mn(n, base)
      return (1 << mn(k, 16)) - 1
    case _:
      h = 16 << (lw-1)
      return (full(lw-1, base, n), full(lw-1, base + h, n))

def loop(A, R, E, F, l, lw, kb, n):
  (E2, any) = count(R, E, F, l, lw, 0, n)
  R2 = step(A, R, R, l, lw, kb)
  if any:
    return loop(A, R2, E2, F, l, lw, kb, n)
  else:
    return E2

def count(R, E, F, lv, lw, base, n):
  switch lv:
    case 0:
      nf = neq(R, F, lw) & (base < n)
      return (E + nf, nf)
    case _:
      (r1, r2) = R
      (e1, e2) = E
      h = 1 << (lv-1)
      (x1, a1) = count(r1, e1, F, lv-1, lw, base, n)
      (x2, a2) = count(r2, e2, F, lv-1, lw, base + h, n)
      return ((x1, x2), a1 | a2)

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

def step(A, T, R, lv, lw, kb):
  switch lv:
    case 0:
      return ort(T, sel(A, R, lw, kb, lw), lw)
    case _:
      (a1, a2) = A
      (t1, t2) = T
      return (step(a1, t1, R, lv-1, lw, kb), step(a2, t2, R, lv-1, lw, kb))

def sel(r, C, j, kb, lw):
  switch j:
    case 0:
      return selw(r, C, kb, lw)
    case _:
      (r1, r2) = r
      (c1, c2) = C
      return ort(sel(r1, c1, j-1, kb, lw), sel(r2, c2, j-1, kb, lw), lw)

def selw(wd, C, k, lw):
  if wd == 0:
    return zt(lw)
  else:
    switch k:
      case 0:
        return C
      case _:
        (c1, c2) = C
        h = 1 << (k-1)
        return ort(selw(wd & ((1 << h) - 1), c1, k-1, lw), selw(wd >> h, c2, k-1, lw), lw)

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))
