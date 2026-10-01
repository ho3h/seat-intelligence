def prog(x):
  return print_expr(x)

def print_expr(e):
  match e:
    case Gexpr/C0:
      return digits(e.f0)
    case Gexpr/C1:
      left = print_expr(e.f0)
      right = print_expr(e.f1)
      return cat([40], cat(left, cat([43], cat(right, [41]))))
    case Gexpr/C2:
      left = print_expr(e.f0)
      right = print_expr(e.f1)
      return cat([40], cat(left, cat([42], cat(right, [41]))))

def digits(n):
  if n < 10:
    return [48 + n]
  else:
    q = n / 10
    r = n % 10
    return cat(digits(q), [48 + r])

def cat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, cat(xs.tail, ys))
