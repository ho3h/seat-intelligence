def prog(x):
  match x:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      return height_node(x)

def height_node(t):
  left = t.f0
  right = t.f2
  match left:
    case Gtree/C0:
      match right:
        case Gtree/C0:
          return 1
        case Gtree/C1:
          return height_node(right) + 1
    case Gtree/C1:
      match right:
        case Gtree/C0:
          return height_node(left) + 1
        case Gtree/C1:
          left_height = height_node(left)
          right_height = height_node(right)
          if left_height > right_height:
            return left_height + 1
          else:
            return right_height + 1
