def prog(x):
  (a, b) = x
  return insert(a, b)

def insert(x, t):
  match t:
    case (0,):
      return (1, (0,), x, (0,))
    case (1, l, v, r):
      if x < v:
        return (1, insert(x, l), v, r)
      else:
        if x > v:
          return (1, l, v, insert(x, r))
        else:
          return t
