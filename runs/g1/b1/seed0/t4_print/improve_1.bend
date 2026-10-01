def prog(x):
  return print_expr(x, [])

def print_expr(e, acc):
  match e:
    case Gexpr/C0:
      return print_digits_rev(e.f0, acc)
    case Gexpr/C1:
      right = print_expr(e.f1, List/Cons(41, acc))
      left = print_expr(e.f0, List/Cons(43, right))
      return List/Cons(40, left)
    case Gexpr/C2:
      right = print_expr(e.f1, List/Cons(41, acc))
      left = print_expr(e.f0, List/Cons(42, right))
      return List/Cons(40, left)

def print_digits_rev(n, acc):
  if n < 10:
    return List/Cons(48 + n, acc)
  else:
    return print_digits_rev(n / 10, List/Cons(48 + (n % 10), acc))
