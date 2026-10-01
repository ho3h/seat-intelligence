def prog(x):
  (xs, t) = x
  return upper_bound(xs, t, 0)

def upper_bound(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head <= t:
        return upper_bound2(xs.tail, t, acc + 1)
      else:
        return acc

def upper_bound2(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head <= t:
        return probe6(xs.tail, t, acc + 1)
      else:
        return acc

def probe6(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head > t:
        return acc
      else:
        match xs.tail:
          case List/Nil:
            return acc + 1
          case List/Cons:
            if xs.tail.head > t:
              return acc + 1
            else:
              return probe4(xs.tail.tail, t, acc + 2)

def probe4(xs, t, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return upper_bound(xs, t, acc)
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return upper_bound(xs, t, acc)
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return upper_bound(xs, t, acc)
                case List/Cons:
                  if c.head <= t:
                    return upper_bound(c.tail, t, acc + 4)
                  else:
                    return upper_bound(xs, t, acc)
