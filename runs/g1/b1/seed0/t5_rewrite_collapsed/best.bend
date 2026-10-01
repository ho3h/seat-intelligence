def prog(x):
  (clusters, edges) = x
  n = length(clusters)
  (tree, rest) = build_tree(clusters, n)
  (keys, total) = collect(edges, tree, n, [], 0)
  ordered = sort(keys)
  distinct = count_unique(ordered, 0, 0, 0)
  return total - distinct

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def build_tree(xs, size):
  if size == 0:
    return (0, xs)
  else:
    if size == 1:
      match xs:
        case List/Nil:
          return (0, xs)
        case List/Cons:
          return (xs.head, xs.tail)
    else:
      left_size = size / 2
      right_size = size - left_size
      (left, rest) = build_tree(xs, left_size)
      (right, rest2) = build_tree(rest, right_size)
      return ((left, right), rest2)

def tree_at(tree, i, size):
  if size <= 1:
    return tree
  else:
    (left, right) = tree
    left_size = size / 2
    if i < left_size:
      return tree_at(left, i, left_size)
    else:
      return tree_at(right, i - left_size, size - left_size)

def collect(edges, tree, n, keys, total):
  match edges:
    case List/Nil:
      return (keys, total)
    case List/Cons:
      (u, v) = edges.head
      cu = tree_at(tree, u, n)
      cv = tree_at(tree, v, n)
      if cu == cv:
        return collect(edges.tail, tree, n, keys, total + 1)
      else:
        if cu < cv:
          key = cu * n + cv
        else:
          key = cv * n + cu
        return collect(edges.tail, tree, n, List/Cons(key, keys), total + 1)

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort(left)
          sorted_right = sort(right)
          return merge(sorted_left, sorted_right)

def merge(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head < b.head:
            return List/Cons(a.head, merge(a.tail, b))
          else:
            return List/Cons(b.head, merge(a, b.tail))

def count_unique(xs, prev, started, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if started == 0:
        return count_unique(xs.tail, xs.head, 1, count + 1)
      else:
        if xs.head == prev:
          return count_unique(xs.tail, prev, started, count)
        else:
          return count_unique(xs.tail, xs.head, started, count + 1)
