type PairTree: Empty | Node { a, b, left, right }

def prog(x):
  (known, cands) = x
  sorted = sort_pairs(known)
  unique = dedup_pairs(sorted)
  n = list_length(unique)
  (tree, _) = build_tree(unique, n)
  return filter_cands(cands, tree)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_pairs(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def pair_less(a, b, c, d):
  if a < c:
    return 1
  else:
    if a == c:
      if b < d:
        return 1
      else:
        return 0
    else:
      return 0

def sort_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          sorted_left = sort_pairs(left)
          sorted_right = sort_pairs(right)
          return merge_pairs(sorted_left, sorted_right)

def merge_pairs(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          (a, b) = xs.head
          (c, d) = ys.head
          if pair_less(c, d, a, b) == 1:
            return List/Cons(ys.head, merge_pairs(xs, ys.tail))
          else:
            return List/Cons(xs.head, merge_pairs(xs.tail, ys))

def dedup_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = xs.head
      return List/Cons(xs.head, dedup_after(xs.tail, a, b))

def dedup_after(xs, a, b):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (c, d) = xs.head
      if a == c:
        if b == d:
          return dedup_after(xs.tail, a, b)
        else:
          return List/Cons(xs.head, dedup_pairs(xs.tail))
      else:
        return List/Cons(xs.head, dedup_pairs(xs.tail))

def build_tree(xs, n):
  if n == 0:
    return (PairTree/Empty, xs)
  else:
    left_n = n / 2
    (left, remaining) = build_tree(xs, left_n)
    match remaining:
      case List/Nil:
        return (PairTree/Empty, [])
      case List/Cons:
        (a, b) = remaining.head
        right_n = n - left_n - 1
        (right, rest) = build_tree(remaining.tail, right_n)
        return (PairTree/Node(a, b, left, right), rest)

def compare_pair(a, b, c, d):
  if a < c:
    return 0
  else:
    if a > c:
      return 2
    else:
      if b < d:
        return 0
      else:
        if b > d:
          return 2
        else:
          return 1

def contains_pair(tree, u, v):
  match tree:
    case PairTree/Empty:
      return 0
    case PairTree/Node:
      order = compare_pair(u, v, tree.a, tree.b)
      if order == 1:
        return 1
      else:
        if order == 0:
          return contains_pair(tree.left, u, v)
        else:
          return contains_pair(tree.right, u, v)

def filter_cands(cands, tree):
  match cands:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = cands.head
      (found, rest) = (contains_pair(tree, u, v), filter_cands(cands.tail, tree))
      if found == 0:
        return List/Cons(cands.head, rest)
      else:
        return rest
