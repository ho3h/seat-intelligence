def prog(x):
  return mirror(x)

def mirror(t):
  switch t.0:
    case 0:
      return (0,)
    case _:
      (_, l, v, r) = t
      mirrored_left = mirror(r)
      mirrored_right = mirror(l)
      return (1, mirrored_left, v, mirrored_right)
