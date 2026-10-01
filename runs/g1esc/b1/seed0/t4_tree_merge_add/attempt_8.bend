def prog(x):
  (a, b) = x
  return merge(a, b)

def merge(a, b):
  match a:
    case (0,):
      return b
    case (1, l1, v1, r1):
      match b:
        case (0,):
          return a
        case (1, l2, v2, r2):
          left = merge(l1, l2)
          value = v1 + v2
          right = merge(r1, r2)
          return (1, left, value, right)
