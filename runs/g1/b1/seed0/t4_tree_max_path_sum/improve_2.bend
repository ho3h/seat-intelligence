def prog(x):
  return max_path(x, 0)

def max_path(t, acc):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      total = acc + t.f1
      match t.f0:
        case Gtree/C0:
          match t.f2:
            case Gtree/C0:
              return total
            case Gtree/C1:
              return max_path(t.f2, total)
        case Gtree/C1:
          left_max = max_path(t.f0, total)
          match t.f2:
            case Gtree/C0:
              return left_max
            case Gtree/C1:
              right_max = max_path(t.f2, total)
              if left_max > right_max:
                return left_max
              else:
                return right_max
