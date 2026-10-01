def prog(input):
  (x, y, t) = input
  return lca(x, y, t)

def lca(x, y, t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      v = t.f1
      if x < v:
        if y < v:
          return lca(x, y, t.f0)
        else:
          return v
      else:
        if x > v:
          if y > v:
            return lca(x, y, t.f2)
          else:
            return v
        else:
          return v
