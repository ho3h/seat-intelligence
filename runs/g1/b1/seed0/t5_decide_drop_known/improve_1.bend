type PairTree: Empty | Node { a, b, left, right }

def prog(x):
  (known, cands) = x
  n = list_length(known)
  sorted = sort_pairs(known)
  (tree, _) = build_tree(sorted, n)
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

def contains_pair(tree, u, v):
  match tree:
    case PairTree/Empty:
      return 0
    case PairTree/Node:
      if u < tree.a:
        return contains_pair(tree.left, u, v)
      else:
        if tree.a < u:
          return contains_pair(tree.right, u, v)
        else:
          if v == tree.b:
            return 1
          else:
            if v < tree.b:
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
