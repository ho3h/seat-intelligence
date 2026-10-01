def prog(x):
  (clusters, edges) = x
  n = list_length(clusters)
  tree = build_tree(clusters, n)
  mapped = map_edges(tree, n, edges)
  return sort_edges(mapped)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def split_at(xs, k):
  if k == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (prefix, rest) = split_at(xs.tail, k - 1)
        return (List/Cons(xs.head, prefix), rest)

def build_tree(xs, n):
  if n == 0:
    return []
  else:
    half = n / 2
    (left_list, rest) = split_at(xs, half)
    match rest:
      case List/Nil:
        return []
      case List/Cons:
        root = rest.head
        right_list = rest.tail
        left_tree = build_tree(left_list, half)
        right_tree = build_tree(right_list, n - half - 1)
        return List/Cons((root, left_tree, right_tree), [])

def lookup_tree(tree, i, n):
  match tree:
    case List/Nil:
      return 0
    case List/Cons:
      (value, left, right) = tree.head
      half = n / 2
      if i < half:
        return lookup_tree(left, i, half)
      else:
        if i == half:
          return value
        else:
          return lookup_tree(right, i - half - 1, n - half - 1)

def map_edges(tree, n, edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      cu = lookup_tree(tree, u, n)
      cv = lookup_tree(tree, v, n)
      rest = map_edges(tree, n, edges.tail)
      if cu == cv:
        return rest
      else:
        if cu < cv:
          return List/Cons((cu, cv), rest)
        else:
          return List/Cons((cv, cu), rest)

def split_edges(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_edges(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
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
