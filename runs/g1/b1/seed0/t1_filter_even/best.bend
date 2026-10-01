def prog(xs):
  return filter_even(xs)

def filter_even(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      ys = xs.tail
      match ys:
        case List/Nil:
          if (xs.head & 1) == 0:
            return List/Cons(xs.head, List/Nil)
          else:
            return List/Nil
        case List/Cons:
          rest = filter_even(ys.tail)
          if (xs.head & 1) == 0:
            if (ys.head & 1) == 0:
              return List/Cons(xs.head, List/Cons(ys.head, rest))
            else:
              return List/Cons(xs.head, rest)
          else:
            if (ys.head & 1) == 0:
              return List/Cons(ys.head, rest)
            else:
              return rest
