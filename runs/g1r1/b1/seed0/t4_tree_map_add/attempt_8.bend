def prog(x):
  (k, tree) = x
  return add_to_tree(tree, k)

def add_to_tree(tree, k):
  match tree:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      return Gtree/C1(add_to_tree(tree.f0, k), tree.f1 + k, add_to_tree(tree.f2, k))
