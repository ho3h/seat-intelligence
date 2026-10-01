def prog(x):
  return print_expr(x, [])

def print_expr(e, acc):
  match e:
    case Gexpr/C0:
      return digits(e.f0, acc)
    case Gexpr/C1:
      right = print_expr(e.f1, List/Cons(41, acc))
      left = print_expr(e.f0, List/Cons(43, right))
      return List/Cons(40, left)
    case Gexpr/C2:
      right = print_expr(e.f1, List/Cons(41, acc))
      left = print_expr(e.f0, List/Cons(42, right))
      return List/Cons(40, left)

def digits(n, acc):
  if n < 10:
    return List/Cons(48 + n, acc)
  else:
    if n < 100:
      return List/Cons(48 + n / 10, List/Cons(48 + n % 10, acc))
    else:
      if n < 1000:
        return List/Cons(48 + n / 100, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc)))
      else:
        if n < 10000:
          return List/Cons(48 + n / 1000, List/Cons(48 + (n / 100) % 10, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc))))
        else:
          if n < 100000:
            return List/Cons(48 + n / 10000, List/Cons(48 + (n / 1000) % 10, List/Cons(48 + (n / 100) % 10, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc)))))
          else:
            if n < 1000000:
              return List/Cons(48 + n / 100000, List/Cons(48 + (n / 10000) % 10, List/Cons(48 + (n / 1000) % 10, List/Cons(48 + (n / 100) % 10, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc))))))
            else:
              if n < 10000000:
                return List/Cons(48 + n / 1000000, List/Cons(48 + (n / 100000) % 10, List/Cons(48 + (n / 10000) % 10, List/Cons(48 + (n / 1000) % 10, List/Cons(48 + (n / 100) % 10, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc)))))))
              else:
                return List/Cons(48 + n / 10000000, List/Cons(48 + (n / 1000000) % 10, List/Cons(48 + (n / 100000) % 10, List/Cons(48 + (n / 10000) % 10, List/Cons(48 + (n / 1000) % 10, List/Cons(48 + (n / 100) % 10, List/Cons(48 + (n / 10) % 10, List/Cons(48 + n % 10, acc))))))))
