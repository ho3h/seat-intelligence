def prog(x):
  (c, edges) = x
  return rewrite_edges(c, edges, [])

def nth(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def insert_weighted(xs, x, y, w):
  match xs:
    case List/Nil:
      return List/Cons((x, y, w), List/Nil)
    case List/Cons:
      (a, b, total) = xs.head
      if x == a:
        if y == b:
          return List/Cons((a, b, total + w), xs.tail)
        else:
          if y < b:
            return List/Cons((x, y, w), xs)
          else:
            return List/Cons(xs.head, insert_weighted(xs.tail, x, y, w))
      else:
        if x < a:
          return List/Cons((x, y, w), xs)
        else:
          return List/Cons(xs.head, insert_weighted(xs.tail, x, y, w))

def rewrite_edges(c, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, w) = edges.head
      cu = nth(c, u)
      cv = nth(c, v)
      if cu == cv:
        return rewrite_edges(c, edges.tail, acc)
      else:
        if cu < cv:
          return rewrite_edges(c, edges.tail, insert_weighted(acc, cu, cv, w))
        else:
          return rewrite_edges(c, edges.tail, insert_weighted(acc, cv, cu, w))
