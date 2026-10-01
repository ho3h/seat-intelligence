def prog(x):
  return tree_hash2(x)

def tree_hash2(t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      match t.f0:
        case Gtree/C0:
          match t.f2:
            case Gtree/C0:
              return 3 * t.f1 + 1
            case Gtree/C1:
              return 3 * t.f1 + 1 + 5 * (2 * tree_hash2(t.f2.f0) + 3 * t.f2.f1 + 5 * tree_hash2(t.f2.f2) + 1)
        case Gtree/C1:
          match t.f2:
            case Gtree/C0:
              return 2 * (2 * tree_hash2(t.f0.f0) + 3 * t.f0.f1 + 5 * tree_hash2(t.f0.f2) + 1) + 3 * t.f1 + 1
            case Gtree/C1:
              return 2 * (2 * tree_hash2(t.f0.f0) + 3 * t.f0.f1 + 5 * tree_hash2(t.f0.f2) + 1) + 3 * t.f1 + 1 + 5 * (2 * tree_hash2(t.f2.f0) + 3 * t.f2.f1 + 5 * tree_hash2(t.f2.f2) + 1)
