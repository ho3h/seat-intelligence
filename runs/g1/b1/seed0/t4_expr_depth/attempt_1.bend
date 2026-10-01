def prog(x):
  return depth(x)

def depth(x):
  match x:
    case Gexpr/C0:
      return 1
    case Gexpr/C1:
      left_depth = depth(x.f0)
      right_depth = depth(x.f1)
      if left_depth > right_depth:
        return left_depth + 1
      else:
        return right_depth + 1
    case Gexpr/C2:
      left_depth = depth(x.f0)
      right_depth = depth(x.f1)
      if left_depth > right_depth:
        return left_depth + 1
      else:
        return right_depth + 1
