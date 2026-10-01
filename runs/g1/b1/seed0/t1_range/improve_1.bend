def prog(n):
  return build(0, n)

def build(i, n):
  if i == n:
    return []
  else:
    j = i + 1
    if j == n:
      return List/Cons(i, [])
    else:
      tail = build(j + 1, n)
      return List/Cons(i, List/Cons(j, tail))
