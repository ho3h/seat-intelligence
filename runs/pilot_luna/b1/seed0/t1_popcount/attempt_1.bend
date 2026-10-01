def prog(n):
  return popcount(n, 0)

def popcount(n, acc):
  if n == 0:
    return acc
  else:
    return popcount(n >> 1, acc + (n & 1))
