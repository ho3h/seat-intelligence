def prog(input):
  (x, tree) = input
  return insert(x, tree)

def insert(x, tree):
  match tree:
    case Gtree/C0:
      return Gtree/C1(Gtree/C0, x, Gtree/C0)
    case Gtree/C1:
      if x < tree.f1:
        return Gtree/C1(insert(x, tree.f0), tree.f1, tree.f2)
      else:
        if x > tree.f1:
          return Gtree/C1(tree.f0, tree.f1, insert(x, tree.f2))
        else:
          return tree
