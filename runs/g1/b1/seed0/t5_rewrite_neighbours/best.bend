def prog(x):
  (k, clusters, edges) = x
  return neighbours(k, clusters, edges, [])

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def insert_sorted(x, xs):
  match xs:
    case List/Nil:
      return List/Cons(x, List/Nil)
    case List/Cons:
      if x == xs.head:
        return xs
      else:
        if x < xs.head:
          return List/Cons(x, xs)
        else:
          return List/Cons(xs.head, insert_sorted(x, xs.tail))

def neighbours(k, clusters, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      a = at(clusters, u)
      b = at(clusters, v)
      if a == k:
        if b == k:
          return neighbours(k, clusters, edges.tail, acc)
        else:
          return neighbours(k, clusters, edges.tail, insert_sorted(b, acc))
      else:
        if b == k:
          return neighbours(k, clusters, edges.tail, insert_sorted(a, acc))
        else:
          return neighbours(k, clusters, edges.tail, acc)
