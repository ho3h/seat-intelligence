def prog(x):
  (tau, cands) = x
  return cnt(cands, tau, 0)

def cnt(xs, tau, acc):
  fold xs with acc:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, s) = xs.head
      return xs.tail(acc + (s >= tau))
