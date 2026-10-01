def prog(tree):
  return post(tree)

def post(tree):
  match tree:
    case Gtree/C0:
      return []
    case Gtree/C1:
      left = post(tree.f0)
      right = post(tree.f2)
      return append(left, append(right, List/Cons(tree.f1, [])))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
