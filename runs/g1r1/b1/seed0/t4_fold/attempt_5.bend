def prog(x):
  return fold_expr(x)

def fold_expr(v):
  match v:
    case Gvexpr/C0:
      return Gvexpr/C0(v.f0)
    case Gvexpr/C1:
      a = fold_expr(v.f0)
      b = fold_expr(v.f1)
      return fold_add(a, b)
    case Gvexpr/C2:
      a = fold_expr(v.f0)
      b = fold_expr(v.f1)
      return fold_mul(a, b)
    case Gvexpr/C3:
      return Gvexpr/C3(v.f0)

def fold_add(a, b):
  match a:
    case Gvexpr/C0:
      match b:
        case Gvexpr/C0:
          return Gvexpr/C0(a.f0 + b.f0)
        case Gvexpr/C1:
          if a.f0 == 0:
            return b
          else:
            return Gvexpr/C1(a, b)
        case Gvexpr/C2:
          if a.f0 == 0:
            return b
          else:
            return Gvexpr/C1(a, b)
        case Gvexpr/C3:
          if a.f0 == 0:
            return b
          else:
            return Gvexpr/C1(a, b)
    case Gvexpr/C1:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return a
          else:
            return Gvexpr/C1(a, b)
        case Gvexpr/C1:
          return Gvexpr/C1(a, b)
        case Gvexpr/C2:
          return Gvexpr/C1(a, b)
        case Gvexpr/C3:
          return Gvexpr/C1(a, b)
    case Gvexpr/C2:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return a
          else:
            return Gvexpr/C1(a, b)
        case Gvexpr/C1:
          return Gvexpr/C1(a, b)
        case Gvexpr/C2:
          return Gvexpr/C1(a, b)
        case Gvexpr/C3:
          return Gvexpr/C1(a, b)
    case Gvexpr/C3:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return a
          else:
            return Gvexpr/C1(a, b)
        case Gvexpr/C1:
          return Gvexpr/C1(a, b)
        case Gvexpr/C2:
          return Gvexpr/C1(a, b)
        case Gvexpr/C3:
          return Gvexpr/C1(a, b)

def fold_mul(a, b):
  match a:
    case Gvexpr/C0:
      match b:
        case Gvexpr/C0:
          return Gvexpr/C0(a.f0 * b.f0)
        case Gvexpr/C1:
          if a.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if a.f0 == 1:
              return b
            else:
              return Gvexpr/C2(a, b)
        case Gvexpr/C2:
          if a.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if a.f0 == 1:
              return b
            else:
              return Gvexpr/C2(a, b)
        case Gvexpr/C3:
          if a.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if a.f0 == 1:
              return b
            else:
              return Gvexpr/C2(a, b)
    case Gvexpr/C1:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if b.f0 == 1:
              return a
            else:
              return Gvexpr/C2(a, b)
        case Gvexpr/C1:
          return Gvexpr/C2(a, b)
        case Gvexpr/C2:
          return Gvexpr/C2(a, b)
        case Gvexpr/C3:
          return Gvexpr/C2(a, b)
    case Gvexpr/C2:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if b.f0 == 1:
              return a
            else:
              return Gvexpr/C2(a, b)
        case Gvexpr/C1:
          return Gvexpr/C2(a, b)
        case Gvexpr/C2:
          return Gvexpr/C2(a, b)
        case Gvexpr/C3:
          return Gvexpr/C2(a, b)
    case Gvexpr/C3:
      match b:
        case Gvexpr/C0:
          if b.f0 == 0:
            return Gvexpr/C0(0)
          else:
            if b.f0 == 1:
              return a
            else:
              return Gvexpr/C2(a, b)
        case Gvexpr/C1:
          return Gvexpr/C2(a, b)
        case Gvexpr/C2:
          return Gvexpr/C2(a, b)
        case Gvexpr/C3:
          return Gvexpr/C2(a, b)
