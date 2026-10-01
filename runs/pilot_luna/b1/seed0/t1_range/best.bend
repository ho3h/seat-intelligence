def prog(n):
  return range_from(0, n)

def range_from(i, remaining):
  switch remaining:
    case 0:
      return []
    case _:
      return List/Cons(i, range_from(i + 1, remaining - 1))
