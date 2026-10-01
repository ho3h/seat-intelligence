# t5_conflict_pairs: the clustering list becomes a balanced tuple tree (ltree: length walk and keyed-set walk in
# parallel). The must-not-link walk runs in parallel: each pair (a, b) is inserted, sorted by b, into bucket a of a
# vertex-keyed tree together with its (future) violation flag c[a] == c[b] (two keyed reads). The buckets'
# structure depends only on the keys, so it is ready before the flags; the output is a tail-threaded in-order
# flatten that keeps flagged pairs (every leaf's conses are independent).
def prog(x):
  (c, mnl) = x
  (C, L, M) = ltree(c)
  B = walkm(mnl, C, L, M, zl(L))
  return fb(B, L, 0, [])

def walkm(ps, C, L, M, B):
  match ps:
    case List/Nil:
      return B
    case List/Cons:
      (a, b) = ps.head
      f = getk(C, a, L, M) == getk(C, b, L, M)
      return walkm(ps.tail, C, L, M, insk(B, a, L, M, b, f))

def insk(t, k, l, m, b, f):
  switch l:
    case 0:
      return ins(t, b, f)
    case _:
      (x, y) = t
      if k & m:
        return (x, insk(y, k, l-1, m >> 1, b, f))
      else:
        return (insk(x, k, l-1, m >> 1, b, f), y)

def ins(xs, b, f):
  match xs:
    case List/Nil:
      return [(b, f)]
    case List/Cons:
      (b2, f2) = xs.head
      if b < b2:
        return List/Cons((b, f), xs)
      else:
        return List/Cons(xs.head, ins(xs.tail, b, f))

def fb(t, l, base, acc):
  switch l:
    case 0:
      return fl(t, base, acc)
    case _:
      (x, y) = t
      h = 1 << (l-1)
      return fb(x, l-1, base, fb(y, l-1, base + h, acc))

def fl(xs, a, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (b, f) = xs.head
      if f:
        return List/Cons((a, b), fl(xs.tail, a, acc))
      else:
        return fl(xs.tail, a, acc)
