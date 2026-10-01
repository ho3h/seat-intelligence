def prog(tree):
  return post_acc(tree, [])

def post_acc(tree, acc):
  match tree:
    case Gtree/C0:
      return acc
    case Gtree/C1:
      return post_acc(tree.f0, post_acc(tree.f2, List/Cons(tree.f1, acc)))
