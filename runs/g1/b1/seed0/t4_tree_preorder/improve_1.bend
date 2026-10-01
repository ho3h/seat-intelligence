def prog(tree):
  return preorder(tree, [])

def preorder(tree, tail):
  match tree:
    case Gtree/C0:
      return tail
    case Gtree/C1:
      return pre_node(tree.f0, tree.f1, tree.f2, tail)

def pre_node(left, value, right, tail):
  match left:
    case Gtree/C0:
      match right:
        case Gtree/C0:
          return List/Cons(value, tail)
        case Gtree/C1:
          right_out = pre_node(right.f0, right.f1, right.f2, tail)
          return List/Cons(value, right_out)
    case Gtree/C1:
      match right:
        case Gtree/C0:
          left_out = pre_node(left.f0, left.f1, left.f2, tail)
          return List/Cons(value, left_out)
        case Gtree/C1:
          right_out = pre_node(right.f0, right.f1, right.f2, tail)
          left_out = pre_node(left.f0, left.f1, left.f2, right_out)
          return List/Cons(value, left_out)
