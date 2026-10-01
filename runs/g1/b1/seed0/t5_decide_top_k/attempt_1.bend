def prog(x):
  (k, cands) = x
  ordered = sort_candidates(cands)
  return take_k(k, ordered)

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

def insert_candidate(item, xs):
  match xs:
    case List/Nil:
      return List/Cons(item, List/Nil)
    case List/Cons:
      if comes_first(item, xs.head) == 1:
        return List/Cons(item, xs)
      else:
        return List/Cons(xs.head, insert_candidate(item, xs.tail))

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      sorted_tail = sort_candidates(xs.tail)
      return insert_candidate(xs.head, sorted_tail)

def take_k(k, xs):
  if k == 0:
    return List/Nil
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        return List/Cons(xs.head, take_k(k - 1, xs.tail))
