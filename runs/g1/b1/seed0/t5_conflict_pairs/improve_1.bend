def prog(x):
  (c, mnl) = x
  sorted_pairs = merge_sort(mnl)
  return filter_violations(c, sorted_pairs)

def split_pairs(xs, side, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if side == 0:
        return split_pairs(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_pairs(xs.tail, 0, left, List/Cons(xs.head, right))

def pair_leq(p, q):
  (a, b) = p
  (c, d) = q
  if a < c:
    return 1
  else:
    if a == c:
      if b <= d:
        return 1
      else:
        return 0
    else:
      return 0

def merge_pairs(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if pair_leq(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_pairs(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_pairs(xs, ys.tail))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs, 0, List/Nil, List/Nil)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_pairs(sorted_left, sorted_right)

def pair_values(xs, a, b, index, value_a):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      if index == b:
        return (value_a, xs.head)
      else:
        if index == a:
          return pair_values(xs.tail, a, b, index + 1, xs.head)
        else:
          return pair_values(xs.tail, a, b, index + 1, value_a)

def filter_violations(c, pairs):
  match pairs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (a, b) = pairs.head
      (value_a, value_b) = pair_values(c, a, b, 0, 0)
      rest = filter_violations(c, pairs.tail)
      if value_a == value_b:
        return List/Cons(pairs.head, rest)
      else:
        return rest
