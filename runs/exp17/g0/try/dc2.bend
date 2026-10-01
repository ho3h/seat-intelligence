def prog(x):
  (tau, cands) = x
  return cnt(cands, tau)

def cnt(xs, tau):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v, s) = xs.head
      return (s >= tau) + cnt(xs.tail, tau)
