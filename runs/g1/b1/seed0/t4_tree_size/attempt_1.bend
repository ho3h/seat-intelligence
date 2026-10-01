def prog(tree):
  match tree:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      return 1 + prog(tree.f0) + prog(tree.f2)
