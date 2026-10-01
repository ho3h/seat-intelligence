def prog(input):
  (x, y, t) = input
  if x < y:
    return lca(x, y, t)
  else:
    return lca(y, x, t)

def lca(lo, hi, t):
  match t:
    case Gtree/C0:
      return 0
    case Gtree/C1:
      v = t.f1
      if hi < v:
        return lca(lo, hi, t.f0)
      else:
        if lo > v:
          return lca(lo, hi, t.f2)
        else:
          return v
