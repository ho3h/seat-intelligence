# t3_reach_count (squaring variant): popcount of row s of the transitive closure, plus s itself.
# Closure by repeated squaring of a bit matrix (no convergence test, so the l
# squarings pipeline). C is ONE tuple tree: l levels keyed by vertex, then lw levels keyed by 16-bit word; leaf =
# word. One walk sets the edge bits with keyed ORs (keys known from the input: the chain collapses). A squaring
# step computes for every v: C'_v = C_v | OR_{w in C_v} C_w, by a divide-and-conquer traversal of v's row
# alongside C (bits select rows; rows OR leafwise). After l steps C covers paths of length 1..2^l >= n, so v is
# cyclic iff bit v of C_v is set. The squarings stop early once one changes nothing.
def prog(x):
  (n, s, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  kb = l - lw
  L = l + lw
  (xx, M) = lvl(1 << L, 0, 1)
  C0 = walk(es, zt(L), lw, L, M)
  C = sqn(C0, l, l, lw, kb)
  (xx, m2) = lvl(1 << l, 0, 1)
  (xy, mw) = lvl(1 << lw, 0, 1)
  R = ork(getk(C, s, l, m2), s >> 4, lw, mw, 1 << (s & 15))
  return pct(R, lw)

def walk(es, C, lw, L, M):
  match es:
    case List/Nil:
      return C
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, ork(C, (u << lw) | (v >> 4), L, M, 1 << (v & 15)), lw, L, M)

# stop early once a squaring changes nothing (closure reached)
def sqn(C, j, l, lw, kb):
  switch j:
    case 0:
      return C
    case _:
      C2 = sq(C, C, l, lw, kb)
      if neq(C, C2, l + lw):
        return sqn(C2, j-1, l, lw, kb)
      else:
        return C2

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

# apply the step to every row of T (vertex levels), each against the whole matrix C
def sq(T, C, lv, lw, kb):
  switch lv:
    case 0:
      return ort(T, sel(T, C, lw, kb, lw), lw)
    case _:
      (a, b) = T
      return (sq(a, C, lv-1, lw, kb), sq(b, C, lv-1, lw, kb))

# OR of the rows of C selected by the bits of row r (r: j word levels; C: j levels of word index, then kb levels)
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

def diag(C, lv, base, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (getk(C, base >> 4, lw, mw) >> (base & 15)) & 1
    case _:
      (a, b) = C
      h = 1 << (lv-1)
      return diag(a, lv-1, base, lw) + diag(b, lv-1, base + h, lw)

def pct(t, l):
  switch l:
    case 0:
      return popc(t)
    case _:
      (a, b) = t
      return pct(a, l-1) + pct(b, l-1)
