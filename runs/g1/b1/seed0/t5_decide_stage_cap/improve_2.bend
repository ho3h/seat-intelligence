def prog(x):
  (tau, cap, cands) = x
  accepted = filter_accepted(cands, tau)
  if cap == 0:
    deferred = count_candidates(accepted)
    return ([], deferred)
  else:
    (ordered, total) = sort_top(accepted, cap)
    pairs = drop_scores(ordered)
    if total > cap:
      return (pairs, total - cap)
    else:
      return (pairs, 0)

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

def sort_top(xs, cap):
  match xs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (xs, 1)
        case List/Cons:
          (left, right) = split_pairs(xs)
          (sorted_left, count_left) = sort_top(left, cap)
          (sorted_right, count_right) = sort_top(right, cap)
          total = count_left + count_right
          if total <= cap:
            return (merge_candidates(sorted_left, sorted_right), total)
          else:
            return (merge_top(sorted_left, sorted_right, cap), total)

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

def merge_top(a, b, remaining):
  if remaining == 0:
    return []
  else:
    match a:
      case List/Nil:
        return take_list(b, remaining)
      case List/Cons:
        match b:
          case List/Nil:
            return take_list(a, remaining)
          case List/Cons:
            if comes_before(a.head, b.head):
              merged = merge_top(a.tail, b, remaining - 1)
              return List/Cons(a.head, merged)
            else:
              merged = merge_top(a, b.tail, remaining - 1)
              return List/Cons(b.head, merged)

def take_list(xs, remaining):
  if remaining == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        tail = take_list(xs.tail, remaining - 1)
        return List/Cons(xs.head, tail)

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

def count_candidates(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_candidates(xs.tail)

def drop_scores(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      tail = drop_scores(xs.tail)
      return List/Cons((u, v), tail)
