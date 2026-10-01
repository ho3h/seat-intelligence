def prog(n):
  if n >= 28:
    return 0
  else:
    return fact(n, 1)

def fact(n, acc):
  switch n:
    case 0:
      return acc
    case _:
      return fact(n - 1, acc * n)
