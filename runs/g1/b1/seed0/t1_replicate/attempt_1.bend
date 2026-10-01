def prog(x):
  (n, v) = x
  return replicate(n, v)

def replicate(n, v):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(v, replicate(n - 1, v))
