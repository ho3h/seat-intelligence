# t5_decide_filter: one list walk; the recursive call is made before the accept test so the test is off the
# walk's critical chain (the walk is the Bend floor, about 9 rounds per cell).
def prog(x):
  (tau, cands) = x
  return filt(tau, cands)

def filt(tau, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = filt(tau, xs.tail)
      (u, v, s) = xs.head
      if s >= tau:
        return List/Cons((u, v, s), rest)
      else:
        return rest
