def prog(x):
  (tau, cap, cands) = x
  ordered = sort_candidates(cands)
  return gather(ordered, tau, cap)

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      sorted_tail = sort_candidates(xs.tail)
      return insert_candidate(xs.head, sorted_tail)

def insert_candidate(item, xs):
  match xs:
    case List/Nil:
      return [item]
    case List/Cons:
      if comes_before(item, xs.head):
        return List/Cons(item, xs)
      else:
        inserted_tail = insert_candidate(item, xs.tail)
        return List/Cons(xs.head, inserted_tail)

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

def gather(xs, tau, remaining):
  match xs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        if remaining > 0:
          (staged_tail, deferred) = gather(xs.tail, tau, remaining - 1)
          return (List/Cons((u, v), staged_tail), deferred)
        else:
          (staged, deferred_tail) = gather(xs.tail, tau, remaining)
          return (staged, deferred_tail + 1)
      else:
        return gather(xs.tail, tau, remaining)
