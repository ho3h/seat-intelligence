def prog(xs):
  return eval_tokens(xs, [])

def eval_tokens(xs, stack):
  match xs:
    case List/Nil:
      match stack:
        case List/Nil:
          return 0
        case List/Cons:
          return stack.head
    case List/Cons:
      (kind, value) = xs.head
      if kind == 0:
        return eval_tokens(xs.tail, List/Cons(value, stack))
      else:
        match stack:
          case List/Nil:
            return 0
          case List/Cons:
            b = stack.head
            match stack.tail:
              case List/Nil:
                return 0
              case List/Cons:
                a = stack.tail.head
                rest = stack.tail.tail
                if value == 43:
                  return eval_tokens(xs.tail, List/Cons(a + b, rest))
                else:
                  if value == 45:
                    return eval_tokens(xs.tail, List/Cons(a - b, rest))
                  else:
                    return eval_tokens(xs.tail, List/Cons(a * b, rest))
