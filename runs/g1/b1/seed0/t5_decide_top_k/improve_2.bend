def prog(x):
  (k, cands) = x
  return quick_top(k, cands, 32)

def quick_top(k, xs, budget):
  if k == 0:
    return List/Nil
  else:
    if budget == 0:
      return take_k(k, merge_sort(xs))
    else:
      match xs:
        case List/Nil:
          return List/Nil
        case List/Cons:
          match xs.tail:
            case List/Nil:
              return xs
            case List/Cons:
              pivot = middle_item(xs, xs)
              (parts, counts) = partition_candidates(pivot, xs)
              (before, equal, after) = parts
              (before_count, equal_count) = counts
              if k <= before_count:
                return quick_top(k, before, budget - 1)
              else:
                sorted_before = quick_top(before_count, before, budget - 1)
                remaining = k - before_count
                if remaining <= equal_count:
                  chosen_equal = take_k(remaining, equal)
                  return append_lists(sorted_before, chosen_equal)
                else:
                  remaining_after = remaining - equal_count
                  sorted_after = quick_top(remaining_after, after, budget - 1)
                  chosen = append_lists(equal, sorted_after)
                  return append_lists(sorted_before, chosen)

def middle_item(slow, fast):
  match fast:
    case List/Nil:
      return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          match fast.tail.tail:
            case List/Nil:
              return slow.head
            case List/Cons:
              return middle_item(slow.tail, fast.tail.tail)

def classify_candidate(item, pivot):
  (u, v, score) = item
  (pu, pv, pscore) = pivot
  if score > pscore:
    return 0
  else:
    if score < pscore:
      return 2
    else:
      if u < pu:
        return 0
      else:
        if u > pu:
          return 2
        else:
          if v < pv:
            return 0
          else:
            if v > pv:
              return 2
            else:
              return 1

def partition_candidates(pivot, xs):
  match xs:
    case List/Nil:
      return ((List/Nil, List/Nil, List/Nil), (0, 0))
    case List/Cons:
      (parts, counts) = partition_candidates(pivot, xs.tail)
      (before, equal, after) = parts
      (before_count, equal_count) = counts
      class = classify_candidate(xs.head, pivot)
      if class == 0:
        return ((List/Cons(xs.head, before), equal, after), (before_count + 1, equal_count))
      else:
        if class == 1:
          return ((before, List/Cons(xs.head, equal), after), (before_count, equal_count + 1))
        else:
          return ((before, equal, List/Cons(xs.head, after)), (before_count, equal_count))

def append_lists(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_lists(a.tail, b))

def take_k(k, xs):
  if k == 0:
    return List/Nil
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        return List/Cons(xs.head, take_k(k - 1, xs.tail))

def split_half(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, List/Nil), List/Nil)
        case List/Cons:
          (left, right) = split_half(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_half(xs)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_candidates(sorted_left, sorted_right)

def merge_candidates(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if comes_first(a.head, b.head):
            return List/Cons(a.head, merge_candidates(a.tail, b))
          else:
            return List/Cons(b.head, merge_candidates(a, b.tail))

def comes_first(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if s1 > s2:
    return 1
  else:
    if s1 < s2:
      return 0
    else:
      if u1 < u2:
        return 1
      else:
        if u1 > u2:
          return 0
        else:
          if v1 < v2:
            return 1
          else:
            return 0
