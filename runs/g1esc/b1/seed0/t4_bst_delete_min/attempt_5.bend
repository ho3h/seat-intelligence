def prog(x):
  return remove_min(x)

def remove_min(node):
  match node:
    case C0:
      return C0
    case C1:
      left = node.f0
      match left:
        case C0:
          return node.f2
        case C1:
          return C1(remove_min(left), node.f1, node.f2)
