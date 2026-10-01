def prog(x):
  (rev, rest) = parse_expr(x, [])
  return reverse_list(rev, [])

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def skip_spaces(xs):
  match xs:
    case List/Nil:
      return xs
    case List/Cons:
      if xs.head == 32:
        return skip_spaces(xs.tail)
      else:
        return xs

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

def parse_factor(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, clean)
    case List/Cons:
      if clean.head == 40:
        (inside, rest) = parse_expr(clean.tail, acc)
        close = skip_spaces(rest)
        match close:
          case List/Nil:
            return (inside, close)
          case List/Cons:
            return (inside, close.tail)
      else:
        (n, rest) = parse_number(clean, 0)
        return (List/Cons((0, n), acc), rest)

def parse_term(xs, acc):
  (first, rest) = parse_factor(xs, acc)
  return parse_term_tail(rest, first)

def parse_term_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, clean)
    case List/Cons:
      if clean.head == 42:
        (next, rest) = parse_factor(clean.tail, acc)
        with_op = List/Cons((1, 42), next)
        return parse_term_tail(rest, with_op)
      else:
        return (acc, clean)

def parse_expr(xs, acc):
  (first, rest) = parse_term(xs, acc)
  return parse_expr_tail(rest, first)

def parse_expr_tail(xs, acc):
  clean = skip_spaces(xs)
  match clean:
    case List/Nil:
      return (acc, clean)
    case List/Cons:
      if clean.head == 43:
        (next, rest) = parse_term(clean.tail, acc)
        with_op = List/Cons((1, 43), next)
        return parse_expr_tail(rest, with_op)
      else:
        return (acc, clean)
