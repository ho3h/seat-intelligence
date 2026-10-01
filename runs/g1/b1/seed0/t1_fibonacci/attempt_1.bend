def prog(n):
  (a, b) = fib_pair(n)
  return a

def fib_pair(n):
  if n == 0:
    return (0, 1)
  else:
    m = n / 2
    (a, b) = fib_pair(m)
    factor = b + b - a
    c = a * factor
    d = a * a + b * b
    if n % 2 == 0:
      return (c, d)
    else:
      return (d, c + d)
