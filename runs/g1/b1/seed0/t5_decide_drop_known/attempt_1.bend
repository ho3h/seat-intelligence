def prog(x):
  (known, cands) = x
  return filter_cands(cands, known)

def filter_cands(cands, known):
  match cands:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = cands.head
      if contains_pair(known, u, v) == 0:
        return List/Cons(cands.head, filter_cands(cands.tail, known))
      else:
        return filter_cands(cands.tail, known)

def contains_pair(known, u, v):
  match known:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = known.head
      if a == u:
        if b == v:
          return 1
        else:
          return contains_pair(known.tail, u, v)
      else:
        return contains_pair(known.tail, u, v)
