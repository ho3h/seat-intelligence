def prog(x):
  (k, t) = x
  return map_tree(t, k)

def map_tree(t, k):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      return Gtree/C1(map_tree(t.f0, k), t.f1 + k, map_tree(t.f2, k))
