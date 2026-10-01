def prog(x):
  (xs, ys) = x
  return zip_add(xs, ys)

def zip_add(xs, ys):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          first = xs.head + ys.head
          xs1 = xs.tail
          ys1 = ys.tail
          match xs1:
            case List/Nil:
              return List/Cons(first, [])
            case List/Cons:
              match ys1:
                case List/Nil:
                  return List/Cons(first, [])
                case List/Cons:
                  second = xs1.head + ys1.head
                  return List/Cons(first, List/Cons(second, zip_add(xs1.tail, ys1.tail)))
