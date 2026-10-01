def prog(tree):
  match tree:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      return prog(tree.f0) + leaf_count(tree.f2)

def leaf_count(tree):
  match tree:
    case Gtree/C0:
      return 1
    case Gtree/C1:
      return leaf_count(tree.f0) + leaf_count(tree.f2)
