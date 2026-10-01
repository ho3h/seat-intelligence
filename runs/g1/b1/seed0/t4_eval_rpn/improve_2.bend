def prog(xs):
  return eval_tokens(xs, (0, 0, 0, []))

def eval_tokens(xs, stack):
  match xs:
    case List/Nil:
      (size, top, second, rest) = stack
      return top
    case List/Cons:
      (kind, value) = xs.head
      (size, top, second, rest) = stack
      if kind == 0:
        if size == 0:
          return eval_tokens(xs.tail, (1, value, 0, []))
        else:
          if size == 1:
            return eval_tokens(xs.tail, (2, value, top, []))
          else:
            return eval_tokens(xs.tail, (2, value, top, List/Cons(second, rest)))
      else:
        result = calculate(second, top, value)
        match rest:
          case List/Nil:
            return eval_tokens(xs.tail, (1, result, 0, []))
          case List/Cons:
            return eval_tokens(xs.tail, (2, result, rest.head, rest.tail))

def calculate(a, b, op):
  if op == 43:
    return a + b
  else:
    if op == 45:
      return a - b
    else:
      return a * b
