def prog(n):
  return build(0, n)

def build(i, n):
  if i == n:
    return []
  else:
    tail = build(i + 1, n)
    return List/Cons(i, tail)
