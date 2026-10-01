def prog(x):
  (out, rest) = parse_expr(x)
  return out

def skip_spaces(xs):
  match xs:
    case List/Nil:
      return xs
    case List/Cons:
      if xs.head == 32:
        return skip_spaces(xs.tail)
      else:
        return xs

def append_list(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_list(a.tail, b))

def parse_number(xs, acc):
  match xs:
    case List/Nil:
      return (acc, xs)
    case List/Cons:
      if xs.head < 48:
        return (acc, xs)
      else:
        if xs.head > 57:
          return (acc, xs)
        else:
          return parse_number(xs.tail, acc * 10 + xs.head - 48)

def parse_factor(xs):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return ([], clean)
    case List/Cons:
      if clean.head == 40:
        (inside, rest) = parse_expr(clean.tail)
        close = skip_spaces(rest)
        match close:
          case List/Nil:
            return (inside, close)
          case List/Cons:
            return (inside, close.tail)
      else:
        (n, rest) = parse_number(clean, 0)
        return (List/Cons((0, n), List/Nil), rest)

def parse_term(xs):
  (left, rest) = parse_factor(xs)
  return parse_term_tail(rest, left)

def parse_term_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, clean)
    case List/Cons:
      if clean.head == 42:
        (right, rest) = parse_factor(clean.tail)
        combined = append_list(acc, right)
        combined = append_list(combined, List/Cons((1, 42), List/Nil))
        return parse_term_tail(rest, combined)
      else:
        return (acc, clean)

def parse_expr(xs):
  (left, rest) = parse_term(xs)
  return parse_expr_tail(rest, left)

def parse_expr_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, clean)
    case List/Cons:
      if clean.head == 43:
        (right, rest) = parse_term(clean.tail)
        combined = append_list(acc, right)
        combined = append_list(combined, List/Cons((1, 43), List/Nil))
        return parse_expr_tail(rest, combined)
      else:
        return (acc, clean)
