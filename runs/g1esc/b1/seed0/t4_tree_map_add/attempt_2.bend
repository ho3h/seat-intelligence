def prog(x):
  (k, t) = x
  return map_tree(t, k)

def map_tree(t, k):
  match t:
    case C0:
      return C0
    case C1:
      return C1(map_tree(t.f0, k), t.f1 + k, map_tree(t.f2, k))
