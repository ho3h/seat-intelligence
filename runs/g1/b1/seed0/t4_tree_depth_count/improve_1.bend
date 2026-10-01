def prog(x):
  (d, t) = x
  return count_pair(t, d)

def count_children(t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      a = t.f0
      b = t.f2
      match a:
        case Gtree/C0:
          match b:
            case Gtree/C0:
              return 0
            case Gtree/C1:
              return 1
        case Gtree/C1:
          match b:
            case Gtree/C0:
              return 1
            case Gtree/C1:
              return 2

def count_pair(t, d):
  if d == 0:
    match t:
      case Gtree/C0:
        return 0
      case Gtree/C1:
        return 1
  else:
    if d == 1:
      return count_children(t)
    else:
      match t:
        case Gtree/C0:
          return 0
        case Gtree/C1:
          a = t.f0
          b = t.f2
          match a:
            case Gtree/C0:
              match b:
                case Gtree/C0:
                  return 0
                case Gtree/C1:
                  left_count = count_pair(b.f0, d - 2)
                  right_count = count_pair(b.f2, d - 2)
                  return left_count + right_count
            case Gtree/C1:
              match b:
                case Gtree/C0:
                  left_count = count_pair(a.f0, d - 2)
                  right_count = count_pair(a.f2, d - 2)
                  return left_count + right_count
                case Gtree/C1:
                  left_count = count_pair(a.f0, d - 2) + count_pair(a.f2, d - 2)
                  right_count = count_pair(b.f0, d - 2) + count_pair(b.f2, d - 2)
                  return left_count + right_count
