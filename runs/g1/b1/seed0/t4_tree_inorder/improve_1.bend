def prog(x):
  match x:
    case Gtree/C0:
      return []
    case Gtree/C1:
      return inorder_acc(x.f0, List/Cons(x.f1, inorder_acc(x.f2, [])))

def inorder_acc(tree, acc):
  match tree:
    case Gtree/C0:
      return acc
    case Gtree/C1:
      return inorder_acc(tree.f0, List/Cons(tree.f1, inorder_acc(tree.f2, acc)))
