def prog(xs):
  return filter_even(xs)

def filter_even(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      t1 = xs.tail
      match t1:
        case List/Nil:
          if xs.head % 2 == 0:
            return List/Cons(xs.head, List/Nil)
          else:
            return List/Nil
        case List/Cons:
          t2 = t1.tail
          match t2:
            case List/Nil:
              return prepend_even_pair(xs.head, t1.head, List/Nil)
            case List/Cons:
              t3 = t2.tail
              match t3:
                case List/Nil:
                  rest = filter_even(t2)
                  return prepend_even_pair(xs.head, t1.head, rest)
                case List/Cons:
                  rest = filter_even(t3.tail)
                  rest = prepend_even_pair(t2.head, t3.head, rest)
                  return prepend_even_pair(xs.head, t1.head, rest)

def prepend_even_pair(a, b, rest):
  if a % 2 == 0:
    if b % 2 == 0:
      return List/Cons(a, List/Cons(b, rest))
    else:
      return List/Cons(a, rest)
  else:
    if b % 2 == 0:
      return List/Cons(b, rest)
    else:
      return rest
