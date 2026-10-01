def prog(x):
  (value, tree) = x
  return insert(value, tree)

def insert(value, tree):
  match tree:
    case Gtree/C0:
      return Gtree/C1(Gtree/C0, value, Gtree/C0)
    case Gtree/C1:
      if value < tree.f1:
        return Gtree/C1(insert(value, tree.f0), tree.f1, tree.f2)
      else:
        if value > tree.f1:
          return Gtree/C1(tree.f0, tree.f1, insert(value, tree.f2))
        else:
          return tree
