def prog(x):
  (k, t) = x
  return map_add(k, t)

def map_add(k, t):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      left = map_add(k, t.f0)
      value = t.f1 + k
      right = map_add(k, t.f2)
      return Gtree/C1(left, value, right)
