def prog(x):
  return depth(x)

def max_depth(a, b):
  if a > b:
    return a
  else:
    return b

def depth(x):
  match x:
    case Gexpr/C0:
      return 1
    case Gexpr/C1:
      return depth_pair(x.f0, x.f1)
    case Gexpr/C2:
      return depth_pair(x.f0, x.f1)

def depth_pair(a, b):
  match a:
    case Gexpr/C0:
      match b:
        case Gexpr/C0:
          return 2
        case Gexpr/C1:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          return max_depth(b0, b1) + 2
        case Gexpr/C2:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          return max_depth(b0, b1) + 2
    case Gexpr/C1:
      a0 = depth(a.f0)
      a1 = depth(a.f1)
      am = max_depth(a0, a1)
      match b:
        case Gexpr/C0:
          return am + 2
        case Gexpr/C1:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          bm = max_depth(b0, b1)
          return max_depth(am, bm) + 2
        case Gexpr/C2:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          bm = max_depth(b0, b1)
          return max_depth(am, bm) + 2
    case Gexpr/C2:
      a0 = depth(a.f0)
      a1 = depth(a.f1)
      am = max_depth(a0, a1)
      match b:
        case Gexpr/C0:
          return am + 2
        case Gexpr/C1:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          bm = max_depth(b0, b1)
          return max_depth(am, bm) + 2
        case Gexpr/C2:
          b0 = depth(b.f0)
          b1 = depth(b.f1)
          bm = max_depth(b0, b1)
          return max_depth(am, bm) + 2
