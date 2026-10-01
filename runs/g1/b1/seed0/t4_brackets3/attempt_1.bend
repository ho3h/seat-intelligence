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
      if c == 40:
        return scan(xs.tail, List/Cons(c, stack), i + 1)
      else:
        if c == 91:
          return scan(xs.tail, List/Cons(c, stack), i + 1)
        else:
          if c == 123:
            return scan(xs.tail, List/Cons(c, stack), i + 1)
          else:
            match stack:
              case List/Nil:
                return i + 1
              case List/Cons:
                if is_match(c, stack.head):
                  return scan(xs.tail, stack.tail, i + 1)
                else:
                  return i + 1

def is_match(close, open):
  if close == 41:
    return open == 40
  else:
    if close == 93:
      return open == 91
    else:
      return open == 123
