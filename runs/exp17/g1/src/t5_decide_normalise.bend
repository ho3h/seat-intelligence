# t5_decide_normalise: bucket sort. A max-id walk (gives the tree depth) and the insertion walk run in parallel;
# each normalised triple is inserted into bucket min(u, v) of a vertex-keyed tuple tree, sorted by max(u, v) and
# merged with max score on equal pairs (keys are input data, so the keyed descents collapse once the depth is
# known; each bucket is a short sorted list). Output: tail-threaded in-order flatten.
def prog(cs):
  (L, M) = lvl(mxw(cs, 0) + 1, 0, 1)
  B = walk(cs, zl(L), L, M)
  return fb(B, L, 0, [])

def mxw(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      (u, v, s) = xs.head
      return mxw(xs.tail, mx(a, mx(u, v)))

def walk(xs, B, L, M):
  match xs:
    case List/Nil:
      return B
    case List/Cons:
      (u, v, s) = xs.head
      return walk(xs.tail, insk(B, mn(u, v), L, M, mx(u, v), s), L, M)

def insk(t, k, l, m, b, s):
  switch l:
    case 0:
      return ins(t, b, s)
    case _:
      (x, y) = t
      if k & m:
        return (x, insk(y, k, l-1, m >> 1, b, s))
      else:
        return (insk(x, k, l-1, m >> 1, b, s), y)

def ins(xs, b, s):
  match xs:
    case List/Nil:
      return [(b, s)]
    case List/Cons:
      (b2, s2) = xs.head
      if b < b2:
        return List/Cons((b, s), xs)
      else:
        if b == b2:
          return List/Cons((b, mx(s, s2)), xs.tail)
        else:
          return List/Cons(xs.head, ins(xs.tail, b, s))

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
      (b, s) = xs.head
      return List/Cons((a, b, s), fl(xs.tail, a, acc))
