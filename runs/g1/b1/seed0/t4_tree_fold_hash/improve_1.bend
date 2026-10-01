def prog(x):
  return tree_hash(x, 24)

def tree_hash(t, budget):
  if budget == 0:
    return 0
  else:
    match t:
      case Gtree/C0:
        return 0
      case Gtree/C1:
        left = tree_hash(t.f0, budget - 1)
        right = tree_hash(t.f2, budget)
        return 2 * left + 3 * t.f1 + 5 * right + 1
