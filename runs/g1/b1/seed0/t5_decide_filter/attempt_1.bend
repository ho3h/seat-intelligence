def prog(x):
  (tau, cands) = x
  return filter_cands(tau, cands)

def filter_cands(tau, cands):
  match cands:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        return List/Cons(cands.head, filter_cands(tau, cands.tail))
      else:
        return filter_cands(tau, cands.tail)
