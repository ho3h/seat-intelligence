def prog(x):
  (k, tree) = x
  return add_to_tree(tree, k)

def add_to_tree(tree, k):
  match tree:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      left = add_to_tree(tree.f0, k)
      value = tree.f1 + k
      right = add_to_tree(tree.f2, k)
      return Gtree/C1(left, value, right)
