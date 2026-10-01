# t5_metric_rand: all pairs in parallel. Both label lists become balanced tuple trees (ltree walks, all four
# walks in parallel), zipped leafwise; pairs are counted by divide and conquer: pairs(Z) = pairs(Z1) + pairs(Z2)
# + cross(Z1, Z2), where cross compares every leaf of Z1 with every leaf of Z2 (all in parallel, balanced sums). Works for arbitrary
# label values (only equality is used).
def prog(x):
  (p, t) = x
  (P, L, M) = ltree(p)
  (T, L2, M2) = ltree(t)
  n = ln(p, 0)
  Z = zip(P, T, L)
  return within(Z, L, 0, n)

def zip(a, b, l):
  switch l:
    case 0:
      return (a, b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (zip(a1, b1, l-1), zip(a2, b2, l-1))

def within(Z, lv, base, n):
  switch lv:
    case 0:
      return 0
    case _:
      (z1, z2) = Z
      h = 1 << (lv-1)
      return within(z1, lv-1, base, n) + within(z2, lv-1, base + h, n) + cross(z1, z2, lv-1, lv-1, base, base + h, n)

def cross(A, B, lv, lb, ba, bb, n):
  if (ba >= n) | (bb >= n):
    return 0
  else:
    return cross_go(A, B, lv, lb, ba, bb, n)

def cross_go(A, B, lv, lb, ba, bb, n):
  switch lv:
    case 0:
      (pi, ti) = A
      if ba < n:
        return inner(B, lb, bb, pi, ti, n)
      else:
        return 0
    case _:
      (a1, a2) = A
      h = 1 << (lv-1)
      return cross(a1, B, lv-1, lb, ba, bb, n) + cross(a2, B, lv-1, lb, ba + h, bb, n)

def inner(W, lv, base, pi, ti, n):
  if base >= n:
    return 0
  else:
    return inner_go(W, lv, base, pi, ti, n)

def inner_go(W, lv, base, pi, ti, n):
  switch lv:
    case 0:
      (pj, tj) = W
      return (pi == pj) == (ti == tj)
    case _:
      (w1, w2) = W
      h = 1 << (lv-1)
      return inner(w1, lv-1, base, pi, ti, n) + inner(w2, lv-1, base + h, pi, ti, n)
