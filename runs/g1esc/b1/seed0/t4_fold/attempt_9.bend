def prog(x):
  return fold(x)

def fold(e):
  match e:
    case vexpr/C0:
      return e
    case vexpr/C3:
      return e
    case vexpr/C1:
      a = fold(e.f0)
      b = fold(e.f1)
      return fold_add(a, b)
    case vexpr/C2:
      a = fold(e.f0)
      b = fold(e.f1)
      return fold_mul(a, b)

def fold_add(a, b):
  match a:
    case vexpr/C0:
      x = a.f0
      match b:
        case vexpr/C0:
          y = b.f0
          return vexpr/C0(x + y)
        case _:
          if x == 0:
            return b
          else:
            return vexpr/C1(a, b)
    case _:
      match b:
        case vexpr/C0:
          y = b.f0
          if y == 0:
            return a
          else:
            return vexpr/C1(a, b)
        case _:
          return vexpr/C1(a, b)

def fold_mul(a, b):
  match a:
    case vexpr/C0:
      x = a.f0
      match b:
        case vexpr/C0:
          y = b.f0
          return vexpr/C0(x * y)
        case _:
          if x == 0:
            return vexpr/C0(0)
          else:
            if x == 1:
              return b
            else:
              return vexpr/C2(a, b)
    case _:
      match b:
        case vexpr/C0:
          y = b.f0
          if y == 0:
            return vexpr/C0(0)
          else:
            if y == 1:
              return a
            else:
              return vexpr/C2(a, b)
        case _:
          return vexpr/C2(a, b)
