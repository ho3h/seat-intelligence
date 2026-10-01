def prog(x):
  (tau, cands) = x
  return count(cands, tau, 0)

def count(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        return count(xs.tail, tau, acc + 1)
      else:
        return count(xs.tail, tau, acc)
