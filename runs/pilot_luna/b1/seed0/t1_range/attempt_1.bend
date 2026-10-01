def prog(n):
  return range_from(0, n)

def range_from(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, range_from(i + 1, n))
