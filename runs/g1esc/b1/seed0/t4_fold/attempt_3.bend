def prog(x):
  return fold_expr(x)

def fold_expr(e):
  match e:
    case Gvexpr/C0:
      return e
    case Gvexpr/C3:
      return e
    case Gvexpr/C1:
      left = fold_expr(e.f0)
      right = fold_expr(e.f1)
      return fold_add(left, right)
    case Gvexpr/C2:
      left = fold_expr(e.f0)
      right = fold_expr(e.f1)
      return fold_mul(left, right)

def fold_add(a, b):
  match a:
    case Gvexpr/C0:
      x = a.f0
      match b:
        case Gvexpr/C0:
          y = b.f0
          return Gvexpr/C0(x + y)
        case _:
          if x == 0:
            return b
          else:
            return Gvexpr/C1(a, b)
    case _:
      match b:
        case Gvexpr/C0:
          y = b.f0
          if y == 0:
            return a
          else:
            return Gvexpr/C1(a, b)
        case _:
          return Gvexpr/C1(a, b)

def fold_mul(a, b):
  match a:
    case Gvexpr/C0:
      x = a.f0
      match b:
        case Gvexpr/C0:
          y = b.f0
          return Gvexpr/C0(x * y)
        case _:
          if x == 0:
            return Gvexpr/C0(0)
          else:
            if x == 1:
              return b
            else:
              return Gvexpr/C2(a, b)
    case _:
      match b:
        case Gvexpr/C0:
          y = b.f0
          if y == 0:
            return Gvexpr/C0(0)
          else:
            if y == 1:
              return a
            else:
              return Gvexpr/C2(a, b)
        case _:
          return Gvexpr/C2(a, b)
