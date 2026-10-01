def prog(x):
  return mirror(x)

def mirror(t):
  switch t.0:
    case 0:
      return (0,)
    case _:
      left = mirror(t.1)
      right = mirror(t.3)
      value = t.2
      return (1, right, value, left)
