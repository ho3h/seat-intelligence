def prog(n):
  return make_range(0, n)

def make_range(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_range(i + 1, n))
