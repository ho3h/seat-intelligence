def prog(x):
  (d, t) = x
  return count_depth(t, d)

def count_depth(t, d):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      if d == 0:
        return 1
      else:
        left_count = count_depth(t.f0, d - 1)
        right_count = count_depth(t.f2, d - 1)
        return left_count + right_count
