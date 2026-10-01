def prog(x):
  (k, xs) = x
  if k == 0:
    return []
  else:
    sorted = sort4(xs, 22)
    return take_n(sorted, k)

def sort4(xs, shift):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          ((ab), (cd)) = split4(xs, shift, [], [], [], [])
          (a, b) = ab
          (c, d) = cd
          if shift == 0:
            return append4(a, b, c, d)
          else:
            sa = sort4(a, shift - 2)
            sb = sort4(b, shift - 2)
            sc = sort4(c, shift - 2)
            sd = sort4(d, shift - 2)
            return append4(sa, sb, sc, sd)

def split4(xs, shift, a, b, c, d):
  match xs:
    case List/Nil:
      return ((a, b), (c, d))
    case List/Cons:
      digit = (xs.head >> shift) & 3
      if digit == 3:
        return split4(xs.tail, shift, List/Cons(xs.head, a), b, c, d)
      else:
        if digit == 2:
          return split4(xs.tail, shift, a, List/Cons(xs.head, b), c, d)
        else:
          if digit == 1:
            return split4(xs.tail, shift, a, b, List/Cons(xs.head, c), d)
          else:
            return split4(xs.tail, shift, a, b, c, List/Cons(xs.head, d))

def append4(a, b, c, d):
  return append(a, append(b, append(c, d)))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      rest = append(xs.tail, ys)
      return List/Cons(xs.head, rest)

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        rest = take_n(xs.tail, n - 1)
        return List/Cons(xs.head, rest)
