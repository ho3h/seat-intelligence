def prog(tree):
  return preorder(tree, [])

def preorder(tree, tail):
  match tree:
    case Gtree/C0:
      return tail
    case Gtree/C1:
      match tree.f0:
        case Gtree/C0:
          return List/Cons(tree.f1, preorder(tree.f2, tail))
        case Gtree/C1:
          right = preorder(tree.f2, tail)
          left = preorder(tree.f0, right)
          return List/Cons(tree.f1, left)
