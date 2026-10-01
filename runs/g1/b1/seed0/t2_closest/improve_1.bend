def prog(input):
  (x, xs) = input
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      d = absdiff(xs.head, x)
      return scan(xs.tail, x, xs.head, d)

def scan(xs, x, best, best_dist):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      (b1, d1) = pick(xs.head, x, best, best_dist)
      match xs.tail:
        case List/Nil:
          return b1
        case List/Cons:
          (b2, d2) = pick(xs.tail.head, x, b1, d1)
          match xs.tail.tail:
            case List/Nil:
              return b2
            case List/Cons:
              (b3, d3) = pick(xs.tail.tail.head, x, b2, d2)
              match xs.tail.tail.tail:
                case List/Nil:
                  return b3
                case List/Cons:
                  (b4, d4) = pick(xs.tail.tail.tail.head, x, b3, d3)
                  return scan(xs.tail.tail.tail.tail, x, b4, d4)

def pick(candidate, x, best, best_dist):
  d = absdiff(candidate, x)
  if d < best_dist:
    return (candidate, d)
  else:
    if d == best_dist:
      if candidate < best:
        return (candidate, d)
      else:
        return (best, best_dist)
    else:
      return (best, best_dist)

def absdiff(a, b):
  if a >= b:
    return a - b
  else:
    return b - a
