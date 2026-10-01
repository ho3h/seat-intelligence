def prog(xs):
  (value, rest) = parse_expr(xs)
  return value

def skip_spaces(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == 32:
        return skip_spaces(xs.tail)
      else:
        return xs

def parse_expr(xs):
  (value, rest) = parse_factor(xs)
  return expr_tail(rest, 0, value)

def expr_tail(xs, sum, product):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (sum + product, [])
    case List/Cons:
      if clean.head == 42:
        (value, rest) = parse_factor(clean.tail)
        return expr_tail(rest, sum, product * value)
      else:
        if clean.head == 43:
          (value, rest) = parse_factor(clean.tail)
          return expr_tail(rest, sum + product, value)
        else:
          return (sum + product, clean)

def parse_factor(xs):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (0, [])
    case List/Cons:
      if clean.head == 40:
        (value, rest) = parse_expr(clean.tail)
        after_spaces = skip_spaces(rest)
        match after_spaces:
          case List/Nil:
            return (value, [])
          case List/Cons:
            return (value, after_spaces.tail)
      else:
        return parse_number(clean, 0)

def parse_number(xs, acc):
  match xs:
    case List/Nil:
      return (acc, [])
    case List/Cons:
      if xs.head >= 48:
        if xs.head <= 57:
          digit = xs.head - 48
          return parse_number(xs.tail, acc * 10 + digit)
        else:
          return (acc, xs)
      else:
        return (acc, xs)
