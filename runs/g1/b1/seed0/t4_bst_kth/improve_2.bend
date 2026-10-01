def prog(x):
  (k, t) = x
  (remaining, found, value) = inorder(k, t)
  return value

def inorder(k, t):
  if k == 0:
    match t:
      case Gtree/C0:
        return (0, 0, 16777215)
      case Gtree/C1:
        return (0, 1, minimum_or(t, t.f1))
  else:
    match t:
      case Gtree/C0:
        return (k, 0, 16777215)
      case Gtree/C1:
        (remaining, found, value) = inorder(k, t.f0)
        if found == 1:
          return (remaining, found, value)
        else:
          if remaining == 1:
            return (0, 1, t.f1)
          else:
            return inorder(remaining - 2, t.f2)

def minimum_or(t, fallback):
  match t:
    case Gtree/C0:
      return fallback
    case Gtree/C1:
      return minimum_or(t.f0, t.f1)
