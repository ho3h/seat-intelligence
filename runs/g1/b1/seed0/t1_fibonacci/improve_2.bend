def prog(n):
  (a, b) = fib_pair(n)
  return a

def fib_pair(n):
  if n < 2:
    if n == 0:
      return (0, 1)
    else:
      return (1, 1)
  else:
    m = n >> 1
    (a, b) = fib_pair(m)
    c = a * (b + b - a)
    d = a * a + b * b
    if n & 1 == 0:
      return (c, d)
    else:
      return (d, c + d)
