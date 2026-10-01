def prog(x):
  (clusters, edges) = x
  mapped = map_edges(clusters, edges)
  return sort_edges(mapped)

def map_edges(clusters, edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      cu = get_cluster(clusters, u)
      cv = get_cluster(clusters, v)
      rest = map_edges(clusters, edges.tail)
      if cu == cv:
        return rest
      else:
        if cu < cv:
          return List/Cons((cu, cv), rest)
        else:
          return List/Cons((cv, cu), rest)

def get_cluster(clusters, i):
  match clusters:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return clusters.head
      else:
        return get_cluster(clusters.tail, i - 1)

def split_edges(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_edges(tail.tail)
          return (List/Cons(xs.head, left), List/Cons(tail.head, right))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_edges(xs)
          sorted_left = sort_edges(left)
          sorted_right = sort_edges(right)
          return merge_unique(sorted_left, sorted_right)

def merge_unique(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          (a, b) = left.head
          (c, d) = right.head
          if a < c:
            rest = merge_unique(left.tail, right)
            return List/Cons(left.head, rest)
          else:
            if a > c:
              rest = merge_unique(left, right.tail)
              return List/Cons(right.head, rest)
            else:
              if b < d:
                rest = merge_unique(left.tail, right)
                return List/Cons(left.head, rest)
              else:
                if b > d:
                  rest = merge_unique(left, right.tail)
                  return List/Cons(right.head, rest)
                else:
                  return merge_unique(left.tail, right.tail)
