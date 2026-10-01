def prog(x):
  (xs, ys) = x
  return dot(xs, ys)

def dot(xs, ys):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match ys:
        case List/Nil:
          return 0
        case List/Cons:
          first = xs.head * ys.head
          match xs.tail:
            case List/Nil:
              return first
            case List/Cons:
              match ys.tail:
                case List/Nil:
                  return first
                case List/Cons:
                  pair = first + xs.tail.head * ys.tail.head
                  return pair + dot(xs.tail.tail, ys.tail.tail)
