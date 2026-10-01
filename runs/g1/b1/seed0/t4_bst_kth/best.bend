def prog(x):
  (k, t) = x
  (remaining, found, value) = inorder(k, t)
  return value

def inorder(k, t):
  match t:
    case Gtree/C0:
      return (k, 0, 16777215)
    case Gtree/C1:
      (remaining, found, value) = inorder(k, t.f0)
      if found == 1:
        return (remaining, found, value)
      else:
        if remaining == 0:
          return (0, 1, t.f1)
        else:
          return inorder(remaining - 1, t.f2)
