def prog(xs):
  return scan(xs, 0)

def scan(xs, acc):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      a = acc + xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return List/Cons(a, List/Nil)
        case List/Cons:
          b = a + t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return List/Cons(a, List/Cons(b, List/Nil))
            case List/Cons:
              c = b + t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Nil)))
                case List/Cons:
                  d = c + t3.head
                  return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, scan(t3.tail, d)))))
