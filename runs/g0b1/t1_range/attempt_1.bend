def prog(x):
  return go(x, [])

def go(n, acc):
  switch n:
    case 0:
      return acc
    case _:
      return go(n-1, List/Cons(n-1, acc))
