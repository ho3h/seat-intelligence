def prog(xs):
  (largest, second) = top_two(xs)
  return second

def top_two(xs):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (xs.head, 0)
        case List/Cons:
          if xs.head >= xs.tail.head:
            a = xs.head
            b = xs.tail.head
          else:
            a = xs.tail.head
            b = xs.head
          (c, d) = top_two(xs.tail.tail)
          if a >= c:
            if b >= c:
              return (a, b)
            else:
              return (a, c)
          else:
            if a >= d:
              return (c, a)
            else:
              return (c, d)
