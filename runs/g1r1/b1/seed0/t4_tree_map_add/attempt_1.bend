def prog(x):
  (k, t) = x
  return map_add(t, k)

def map_add(t, k):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      return Gtree/C1(map_add(t.f0, k), t.f1 + k, map_add(t.f2, k))
