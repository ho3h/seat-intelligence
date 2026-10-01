type Gtree:
  C0
  C1 { f0, f1, f2 }

def prog(x):
  return remove_min(x)

def remove_min(node):
  match node:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      left = node.f0
      match left:
        case Gtree/C0:
          return node.f2
        case Gtree/C1:
          return Gtree/C1(remove_min(left), node.f1, node.f2)
