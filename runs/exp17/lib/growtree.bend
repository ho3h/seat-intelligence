# ---- growtree: read a list into an index-keyed tuple-tree without knowing its length: MSB-first keys, and when
# i reaches 2^l the tree becomes (tree, zeros). Keyed puts pipeline behind the list read. -> (n, tree, depth)
def grow(T, g, l):
  switch g:
    case 0:
      return T
    case _:
      return (T, zt(l))

def put(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, put(b, k, l-1, m >> 1, v))
      else:
        return (put(a, k, l-1, m >> 1, v), b)

def gwalk(xs, i, T, l, p):
  match xs:
    case List/Nil:
      return (i, T, l)
    case List/Cons:
      g = (i == p) & (i > 0)
      l2 = l + g
      p2 = p << g
      return gwalk(xs.tail, i + 1, put(grow(T, g, l), i, l2, p2 >> 1, xs.head), l2, p2)
