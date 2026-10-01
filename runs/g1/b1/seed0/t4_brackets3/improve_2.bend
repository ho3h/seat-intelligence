def prog(xs):
  return scan(xs, [], 1)

def scan(xs, stack, pos):
  match xs:
    case List/Nil:
      match stack:
        case List/Nil:
          return 0
        case List/Cons:
          return pos
    case List/Cons:
      c = xs.head
      if c == 40:
        return scan(xs.tail, List/Cons(41, stack), pos + 1)
      else:
        if c == 91:
          return scan(xs.tail, List/Cons(93, stack), pos + 1)
        else:
          if c == 123:
            return scan(xs.tail, List/Cons(125, stack), pos + 1)
          else:
            match stack:
              case List/Nil:
                return pos
              case List/Cons:
                if c == stack.head:
                  return scan(xs.tail, stack.tail, pos + 1)
                else:
                  return pos
