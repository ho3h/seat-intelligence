def prog(x):
  return fold_raw(x)

def fold_raw(e):
  match e:
    case (0, n):
      return (0, n)
    case (3, i):
      return (3, i)
    case (1, a, b):
      fa = fold_raw(a)
      fb = fold_raw(b)
      return fold_add_raw(fa, fb)
    case (2, a, b):
      fa = fold_raw(a)
      fb = fold_raw(b)
      return fold_mul_raw(fa, fb)
    case _:
      return e

def fold_add_raw(a, b):
  match a:
    case (0, x):
      match b:
        case (0, y):
          return (0, x + y)
        case _:
          if x == 0:
            return b
          else:
            return (1, a, b)
    case _:
      match b:
        case (0, y):
          if y == 0:
            return a
          else:
            return (1, a, b)
        case _:
          return (1, a, b)

def fold_mul_raw(a, b):
  match a:
    case (0, x):
      match b:
        case (0, y):
          return (0, x * y)
        case _:
          if x == 0:
            return (0, 0)
          else:
            if x == 1:
              return b
            else:
              return (2, a, b)
    case _:
      match b:
        case (0, y):
          if y == 0:
            return (0, 0)
          else:
            if y == 1:
              return a
            else:
              return (2, a, b)
        case _:
          return (2, a, b)
