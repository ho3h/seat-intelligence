def prog(x):
  (p, xs) = x
  return part(p, xs)

def part(p, xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (lo, hi) = part(p, xs.tail)
      h = xs.head
      if h < p:
        return (List/Cons(h, lo), hi)
      else:
        return (lo, List/Cons(h, hi))
