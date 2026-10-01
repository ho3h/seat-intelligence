def prog(tree):
  return delete_min(tree)

def delete_min(tree):
  match tree:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      match tree.f0:
        case Gtree/C0:
          return tree.f2
        case Gtree/C1:
          return Gtree/C1(delete_min(tree.f0), tree.f1, tree.f2)
