def prog(x):
  return inorder_acc(x, [])

def inorder_acc(tree, acc):
  match tree:
    case Gtree/C0:
      return acc
    case Gtree/C1:
      right = inorder_acc(tree.f2, acc)
      with_node = List/Cons(tree.f1, right)
      return inorder_acc(tree.f0, with_node)
