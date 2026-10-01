def prog(xs):
  return map_double(xs)

def map_double(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      a = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return List/Cons(a * 2, List/Nil)
        case List/Cons:
          b = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return List/Cons(a * 2, List/Cons(b * 2, List/Nil))
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return List/Cons(a * 2, List/Cons(b * 2, List/Cons(c * 2, List/Nil)))
                case List/Cons:
                  d = t3.head
                  return List/Cons(a * 2, List/Cons(b * 2, List/Cons(c * 2, List/Cons(d * 2, map_double(t3.tail)))))
