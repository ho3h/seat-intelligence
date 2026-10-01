def prog(xs):
  (tree, rest) = parse_expr(xs)
  return tree

def skip_spaces(xs):
  match xs:
    case List/Nil:
      return xs
    case List/Cons:
      if xs.head == 32:
        return skip_spaces(xs.tail)
      else:
        return xs

def parse_expr(xs):
  (left, rest) = parse_term(xs)
  return parse_expr_tail(left, rest)

def parse_expr_tail(acc, xs):
  rest = skip_spaces(xs)
  match rest:
    case List/Nil:
      return (acc, rest)
    case List/Cons:
      if rest.head == 43:
        (right, tail) = parse_term(rest.tail)
        return parse_expr_tail(Gexpr/C1(acc, right), tail)
      else:
        return (acc, rest)

def parse_term(xs):
  (left, rest) = parse_factor(xs)
  return parse_term_tail(left, rest)

def parse_term_tail(acc, xs):
  rest = skip_spaces(xs)
  match rest:
    case List/Nil:
      return (acc, rest)
    case List/Cons:
      if rest.head == 42:
        (right, tail) = parse_factor(rest.tail)
        return parse_term_tail(Gexpr/C2(acc, right), tail)
      else:
        return (acc, rest)

def parse_factor(xs):
  rest = skip_spaces(xs)
  match rest:
    case List/Nil:
      return (Gexpr/C0(0), rest)
    case List/Cons:
      if rest.head == 40:
        (tree, after_expr) = parse_expr(rest.tail)
        after_close = skip_spaces(after_expr)
        match after_close:
          case List/Nil:
            return (tree, after_close)
          case List/Cons:
            return (tree, after_close.tail)
      else:
        (value, tail) = parse_number(rest, 0)
        return (Gexpr/C0(value), tail)

def parse_number(xs, acc):
  match xs:
    case List/Nil:
      return (acc, xs)
    case List/Cons:
      if xs.head >= 48:
        if xs.head <= 57:
          digit = xs.head - 48
          return parse_number(xs.tail, acc * 10 + digit)
        else:
          return (acc, xs)
      else:
        return (acc, xs)
