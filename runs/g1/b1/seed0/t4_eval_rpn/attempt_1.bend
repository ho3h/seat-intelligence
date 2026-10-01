def prog(xs):
  return run_tokens(xs, [])

def run_tokens(xs, stack):
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
        return run_tokens(xs.tail, List/Cons(value, stack))
      else:
        return apply_operator(xs.tail, stack, value)

def apply_operator(xs, stack, op):
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
          result = calculate(a, b, op)
          return run_tokens(xs, List/Cons(result, rest))

def calculate(a, b, op):
  if op == 43:
    return a + b
  else:
    if op == 45:
      return a - b
    else:
      return a * b
