def prog(xs):
  return min_list(xs, 16777215)

def min2(a, b):
  if a < b:
    return a
  else:
    return b

def min4(a, b, c, d):
  return min2(min2(a, b), min2(c, d))

def min_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return min2(acc, xs.head)
        case List/Cons:
          match xs.tail.tail:
            case List/Nil:
              return min2(acc, min2(xs.head, xs.tail.head))
            case List/Cons:
              match xs.tail.tail.tail:
                case List/Nil:
                  return min2(acc, min2(min2(xs.head, xs.tail.head), xs.tail.tail.head))
                case List/Cons:
                  group_min = min4(xs.head, xs.tail.head, xs.tail.tail.head, xs.tail.tail.tail.head)
                  return min_list(xs.tail.tail.tail.tail, min2(acc, group_min))
