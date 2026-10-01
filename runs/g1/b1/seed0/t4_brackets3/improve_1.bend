def prog(xs):
  return scan(xs, [], 0)

def scan(xs, stack, i):
  match xs:
    case List/Nil:
      match stack:
        case List/Nil:
          return 0
        case List/Cons:
          return i + 1
    case List/Cons:
      c = xs.head
      is_open = (c == 40) | (c == 91) | (c == 123)
      if is_open:
        return scan(xs.tail, List/Cons(c, stack), i + 1)
      else:
        match stack:
          case List/Nil:
            return i + 1
          case List/Cons:
            if c == 41:
              if stack.head == 40:
                return scan(xs.tail, stack.tail, i + 1)
              else:
                return i + 1
            else:
              if c == stack.head + 2:
                return scan(xs.tail, stack.tail, i + 1)
              else:
                return i + 1
