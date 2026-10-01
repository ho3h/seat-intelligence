def prog(x):
  match x:
    case Gtree/C0:
      return []
    case Gtree/C1:
      return inorder_node(x.f0, x.f1, x.f2, [])

def inorder_node(left, value, right, acc):
  match right:
    case Gtree/C0:
      next = List/Cons(value, acc)
      match left:
        case Gtree/C0:
          return next
        case Gtree/C1:
          return inorder_node(left.f0, left.f1, left.f2, next)
    case Gtree/C1:
      right_acc = inorder_node(right.f0, right.f1, right.f2, acc)
      next = List/Cons(value, right_acc)
      match left:
        case Gtree/C0:
          return next
        case Gtree/C1:
          return inorder_node(left.f0, left.f1, left.f2, next)
