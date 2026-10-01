# t5_decide_singleton: one pass, branch-free running max (stored +1 so the first entry always wins).
def prog(x):
  (tau, probs) = x
  return go(probs, 0, 6, 0, tau)

def go(xs, i, bi, bv, tau):
  match xs:
    case List/Nil:
      return bi + (bv <= tau) * (6 - bi)
    case List/Cons:
      h = xs.head + 1
      t = h > bv
      return go(xs.tail, i + 1, bi + t * (i - bi), bv + t * (h - bv), tau)
