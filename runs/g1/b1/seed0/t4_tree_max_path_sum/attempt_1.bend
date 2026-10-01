def prog(x):
  return max_path(x, 0)

def is_leaf(t):
  match t:
    case Gtree/C0:
      return 1
    case Gtree/C1:
      return 0

def max_path(t, acc):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      total = acc + t.f1
      if is_leaf(t.f0) == 1:
        if is_leaf(t.f2) == 1:
          return total
        else:
          return max_path(t.f2, total)
      else:
        left_max = max_path(t.f0, total)
        right_max = max_path(t.f2, total)
        if left_max > right_max:
          return left_max
        else:
          return right_max
