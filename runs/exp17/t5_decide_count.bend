def prog(x):
  (tau, cands) = x
  return cnt(cands, tau, 0)

def cnt(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, s) = xs.head
      return cnt(xs.tail, tau, acc + (s >= tau))
