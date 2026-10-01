def prog(x):
  return tree_hash(x)

def tree_hash(t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      left = tree_hash(t.f0)
      right = tree_hash(t.f2)
      return 2 * left + 3 * t.f1 + 5 * right + 1
