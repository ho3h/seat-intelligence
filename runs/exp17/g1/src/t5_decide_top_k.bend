# t5_decide_top_k: bucket sort + a parallel prefix take. Each triple is inserted into bucket 1000 - score of a
# 10-level tuple tree (score 0..1000 by contract; keys are input data, so the descents collapse level by level),
# sorted by (u, v) within the bucket. Subtree sizes are annotated bottom-up; take(k) then splits k at every node
# (left gets min(k, size_left), right gets the rest) and emits tail-threaded, so all leaves work in parallel.
def prog(x):
  (k, cs) = x
  B = walk(cs, zl(10), 10, 512)
  (T, sz) = ann(B, 10)
  return take(T, 10, k, [])

def walk(xs, B, L, M):
  match xs:
    case List/Nil:
      return B
    case List/Cons:
      (u, v, s) = xs.head
      return walk(xs.tail, insk(B, 1000 - s, L, M, (u, v, s)), L, M)

def insk(t, k, l, m, e):
  switch l:
    case 0:
      return ins(t, e)
    case _:
      (x, y) = t
      if k & m:
        return (x, insk(y, k, l-1, m >> 1, e))
      else:
        return (insk(x, k, l-1, m >> 1, e), y)

def ins(xs, e):
  match xs:
    case List/Nil:
      return [e]
    case List/Cons:
      (u, v, s) = e
      (u2, v2, s2) = xs.head
      if (u < u2) | ((u == u2) & (v <= v2)):
        return List/Cons(e, xs)
      else:
        return List/Cons(xs.head, ins(xs.tail, e))

def len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len(xs.tail)

# node -> (left, right, size of left); leaf -> (list, size)
def ann(t, l):
  switch l:
    case 0:
      return (t, len(t))
    case _:
      (x, y) = t
      (x2, sx) = ann(x, l-1)
      (y2, sy) = ann(y, l-1)
      return ((x2, y2, sx), sx + sy)

def take(t, l, k, acc):
  if k == 0:
    return acc
  else:
    switch l:
      case 0:
        return tk(t, k, acc)
      case _:
        (x, y, sx) = t
        k1 = mn(k, sx)
        return take(x, l-1, k1, take(y, l-1, k - k1, acc))

def tk(xs, k, acc):
  if k == 0:
    return acc
  else:
    match xs:
      case List/Nil:
        return acc
      case List/Cons:
        return List/Cons(xs.head, tk(xs.tail, k - 1, acc))
