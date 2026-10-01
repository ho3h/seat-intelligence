def prog(x):
  (clusters, edges) = x
  directed = make_incidences(clusters, edges, [])
  ordered = merge_sort(directed)
  distinct = unique_pairs(ordered, 0, 0, 1)
  return emit_degrees(clusters, distinct, 0)

def make_incidences(clusters, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      a = lookup(clusters, u)
      b = lookup(clusters, v)
      if a == b:
        return make_incidences(clusters, edges.tail, acc)
      else:
        if a < b:
          next = List/Cons((a, b), List/Cons((b, a), acc))
          return make_incidences(clusters, edges.tail, next)
        else:
          next = List/Cons((b, a), List/Cons((a, b), acc))
          return make_incidences(clusters, edges.tail, next)

def lookup(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return lookup(xs.tail, index - 1)

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternating(xs)
          return merge_pairs(merge_sort(left), merge_sort(right))

def split_alternating(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alternating(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_pairs(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if pair_leq(left.head, right.head) == 1:
            return List/Cons(left.head, merge_pairs(left.tail, right))
          else:
            return List/Cons(right.head, merge_pairs(left, right.tail))

def pair_leq(a, b):
  (a0, a1) = a
  (b0, b1) = b
  if a0 < b0:
    return 1
  else:
    if a0 == b0:
      if a1 <= b1:
        return 1
      else:
        return 0
    else:
      return 0

def unique_pairs(xs, prev0, prev1, first):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = xs.head
      if first == 1:
        return List/Cons(xs.head, unique_pairs(xs.tail, a, b, 0))
      else:
        if a == prev0:
          if b == prev1:
            return unique_pairs(xs.tail, prev0, prev1, 0)
          else:
            return List/Cons(xs.head, unique_pairs(xs.tail, a, b, 0))
        else:
          return List/Cons(xs.head, unique_pairs(xs.tail, a, b, 0))

def emit_degrees(clusters, incidences, index):
  match clusters:
    case List/Nil:
      return []
    case List/Cons:
      rest = emit_degrees(clusters.tail, incidences, index + 1)
      if clusters.head == index:
        (degree, remaining) = count_target(incidences, index, 0)
        rest = emit_degrees(clusters.tail, remaining, index + 1)
        return List/Cons(degree, rest)
      else:
        return rest

def count_target(incidences, target, count):
  match incidences:
    case List/Nil:
      return (count, [])
    case List/Cons:
      (a, b) = incidences.head
      if a == target:
        return count_target(incidences.tail, target, count + 1)
      else:
        return (count, incidences)
