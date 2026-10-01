def prog(x):
  (k, xs) = x
  return filt4(k, xs)

def keep(k, a, xs):
  if a > k:
    return List/Cons(a, xs)
  else:
    return xs

def small(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = small(k, xs.tail)
      return keep(k, xs.head, rest)

def filt4(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      t = xs.tail
      match t:
        case List/Nil:
          return small(k, xs)
        case List/Cons:
          b = t.head
          u = t.tail
          match u:
            case List/Nil:
              return small(k, xs)
            case List/Cons:
              c = u.head
              v = u.tail
              match v:
                case List/Nil:
                  return small(k, xs)
                case List/Cons:
                  d = v.head
                  rest = filt4(k, v.tail)
                  rest = keep(k, d, rest)
                  rest = keep(k, c, rest)
                  rest = keep(k, b, rest)
                  return keep(k, a, rest)
