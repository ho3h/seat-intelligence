def prog(x):
  (tau, probs) = x
  (bi, bv) = best(probs, 0)
  return bi + (bv < tau) * (6 - bi)

# returns (index, value) of the max, lowest index on ties; empty list gives (6, 0) never chosen over a real entry
def best(xs, i):
  match xs:
    case List/Nil:
      return (6, 0)
    case List/Cons:
      (j, w) = best(xs.tail, i + 1)
      t = w > xs.head
      return (i + t * (j - i), xs.head + t * (w - xs.head))
