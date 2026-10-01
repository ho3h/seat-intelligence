def prog(x):
  return height(x)

def height(t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      left = height(t.f0)
      right = height(t.f2)
      if left > right:
        return left + 1
      else:
        return right + 1
