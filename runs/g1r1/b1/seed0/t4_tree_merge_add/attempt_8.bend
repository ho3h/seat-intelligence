def prog(x):
  (a, b) = x
  return merge_tree(a, b)

def merge_tree(a, b):
  match a:
    case Gtree/C0:
      return b
    case Gtree/C1:
      match b:
        case Gtree/C0:
          return a
        case Gtree/C1:
          left = merge_tree(a.f0, b.f0)
          value = a.f1 + b.f1
          right = merge_tree(a.f2, b.f2)
          return Gtree/C1(left, value, right)
