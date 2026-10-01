def prog(t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      left = prog(t.f0)
      right = prog(t.f2)
      if left > right:
        return left + 1
      else:
        return right + 1
