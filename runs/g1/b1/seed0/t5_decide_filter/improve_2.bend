def prog(x):
  (tau, cands) = x
  return filter4(tau, cands)

def put_if(tau, item, rest):
  (u, v, score) = item
  if score >= tau:
    return List/Cons(item, rest)
  else:
    return rest

def filter1(tau, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = filter1(tau, xs.tail)
      return put_if(tau, xs.head, rest)

def filter4(tau, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      match xs.tail:
        case List/Nil:
          return filter1(tau, xs)
        case List/Cons:
          b = xs.tail.head
          match xs.tail.tail:
            case List/Nil:
              return filter1(tau, xs)
            case List/Cons:
              c = xs.tail.tail.head
              match xs.tail.tail.tail:
                case List/Nil:
                  return filter1(tau, xs)
                case List/Cons:
                  d = xs.tail.tail.tail.head
                  rest = filter4(tau, xs.tail.tail.tail.tail)
                  r_d = put_if(tau, d, rest)
                  r_c = put_if(tau, c, r_d)
                  r_b = put_if(tau, b, r_c)
                  return put_if(tau, a, r_b)
