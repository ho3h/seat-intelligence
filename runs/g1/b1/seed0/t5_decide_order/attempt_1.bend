def prog(x):
  (tau, cands) = x
  return process(cands, tau, [])

def process(cands, tau, acc):
  match cands:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        return process(cands.tail, tau, insert(cands.head, acc))
      else:
        return process(cands.tail, tau, acc)

def insert(item, sorted):
  match sorted:
    case List/Nil:
      return List/Cons(item, List/Nil)
    case List/Cons:
      (iu, iv, iscore) = item
      (hu, hv, hscore) = sorted.head
      if iscore > hscore:
        return List/Cons(item, sorted)
      else:
        if iscore == hscore:
          if iu < hu:
            return List/Cons(item, sorted)
          else:
            if iu == hu:
              if iv < hv:
                return List/Cons(item, sorted)
              else:
                return List/Cons(sorted.head, insert(item, sorted.tail))
            else:
              return List/Cons(sorted.head, insert(item, sorted.tail))
        else:
          return List/Cons(sorted.head, insert(item, sorted.tail))
