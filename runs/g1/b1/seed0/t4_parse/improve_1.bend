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
  (first, rest) = parse_factor(xs)
  return parse_ops(first, first, 0, rest)

def parse_ops(term, add_acc, has_add, xs):
  match xs:
    case List/Nil:
      return finish_expr(term, add_acc, has_add, xs)
    case List/Cons:
      if xs.head == 32:
        return parse_ops(term, add_acc, has_add, xs.tail)
      else:
        if xs.head == 42:
          (right, tail) = parse_factor(xs.tail)
          return parse_ops(Gexpr/C2(term, right), add_acc, has_add, tail)
        else:
          if xs.head == 43:
            if has_add == 0:
              next_add = term
            else:
              next_add = Gexpr/C1(add_acc, term)
            (right, tail) = parse_factor(xs.tail)
            return parse_ops(right, next_add, 1, tail)
          else:
            return finish_expr(term, add_acc, has_add, xs)

def finish_expr(term, add_acc, has_add, xs):
  if has_add == 0:
    return (term, xs)
  else:
    return (Gexpr/C1(add_acc, term), xs)

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
