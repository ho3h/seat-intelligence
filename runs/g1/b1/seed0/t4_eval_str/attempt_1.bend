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

def drop_one(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return xs.tail

def parse_expr(xs):
  clean = skip_spaces(xs)
  (value, rest) = parse_term(clean)
  return expr_tail(rest, value)

def expr_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, [])
    case List/Cons:
      if clean.head == 43:
        (value, rest) = parse_term(clean.tail)
        return expr_tail(rest, acc + value)
      else:
        return (acc, clean)

def parse_term(xs):
  clean = skip_spaces(xs)
  (value, rest) = parse_factor(clean)
  return term_tail(rest, value)

def term_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, [])
    case List/Cons:
      if clean.head == 42:
        (value, rest) = parse_factor(clean.tail)
        return term_tail(rest, acc * value)
      else:
        return (acc, clean)

def parse_factor(xs):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (0, [])
    case List/Cons:
      if clean.head == 40:
        (value, rest) = parse_expr(clean.tail)
        after_spaces = skip_spaces(rest)
        return (value, drop_one(after_spaces))
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
