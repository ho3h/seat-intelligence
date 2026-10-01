def prog(x):
  (a, b) = x
  return merge(a, b)

def merge(a, b):
  match a:
    case C0:
      return b
    case C1:
      match b:
        case C0:
          return a
        case C1:
          left = merge(a.f0, b.f0)
          value = a.f1 + b.f1
          right = merge(a.f2, b.f2)
          return C1(left, value, right)
