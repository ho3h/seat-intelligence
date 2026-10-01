def prog(xs):
  (largest, second) = fast_top_two(xs)
  return second

def offer(value, largest, second):
  if value >= largest:
    return (value, largest)
  else:
    if value > second:
      return (largest, value)
    else:
      return (largest, second)

def slow_top_two(xs, largest, second):
  match xs:
    case List/Nil:
      return (largest, second)
    case List/Cons:
      (next_largest, next_second) = offer(xs.head, largest, second)
      return slow_top_two(xs.tail, next_largest, next_second)

def fast_top_two(xs):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return offer(xs.head, 0, 0)
        case List/Cons:
          match xs.tail.tail:
            case List/Nil:
              (a, b) = offer(xs.head, 0, 0)
              return offer(xs.tail.head, a, b)
            case List/Cons:
              match xs.tail.tail.tail:
                case List/Nil:
                  (a, b) = offer(xs.head, 0, 0)
                  (c, d) = offer(xs.tail.head, a, b)
                  return offer(xs.tail.tail.head, c, d)
                case List/Cons:
                  (a, b) = fast_top_two(xs.tail.tail.tail.tail)
                  (c, d) = offer(xs.head, a, b)
                  (e, f) = offer(xs.tail.head, c, d)
                  (g, h) = offer(xs.tail.tail.head, e, f)
                  return offer(xs.tail.tail.tail.head, g, h)
