def prog(x):
  return mirror(x)

def mirror(t):
  switch t.0:
    case 0:
      return (0,)
    case _:
      left = t.1
      value = t.2
      right = t.3
      return (1, mirror(right), value, mirror(left))
