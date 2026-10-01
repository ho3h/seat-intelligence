def prog(xs):
  return max_list(xs)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def max_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      a = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return a
        case List/Cons:
          b = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return max2(a, b)
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return max2(max2(a, b), c)
                case List/Cons:
                  d = t3.head
                  t4 = t3.tail
                  block = max2(max2(a, b), max2(c, d))
                  rest = max_list(t4)
                  return max2(block, rest)
