def prog(x):
  return mirror(x)

def mirror(t):
  switch t.0:
    case 0:
      return (0,)
    case _:
      (_, left, value, right) = t
      return (1, mirror(right), value, mirror(left))
