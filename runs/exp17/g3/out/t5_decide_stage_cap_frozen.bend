def prog(x):
  (tau, cap, cands) = x
  accepted = filter_accepted(cands, tau)
  ordered = sort_candidates(accepted)
  return stage(ordered, cap)

def filter_accepted(xs, tau):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      accepted_tail = filter_accepted(xs.tail, tau)
      (u, v, score) = xs.head
      if score >= tau:
        return List/Cons(xs.head, accepted_tail)
      else:
        return accepted_tail

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          sorted_left = sort_candidates(left)
          sorted_right = sort_candidates(right)
          return merge_candidates(sorted_left, sorted_right)

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

def merge_candidates(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if comes_before(a.head, b.head):
            merged = merge_candidates(a.tail, b)
            return List/Cons(a.head, merged)
          else:
            merged = merge_candidates(a, b.tail)
            return List/Cons(b.head, merged)

def comes_before(a, b):
  (ua, va, sa) = a
  (ub, vb, sb) = b
  if sa == sb:
    if ua == ub:
      return va < vb
    else:
      return ua < ub
  else:
    return sa > sb

def stage(xs, cap):
  match xs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      if cap > 0:
        (staged_tail, deferred) = stage(xs.tail, cap - 1)
        (u, v, score) = xs.head
        return (List/Cons((u, v), staged_tail), deferred)
      else:
        return ([], count_candidates(xs))

def count_candidates(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_candidates(xs.tail)
