def prog(n):
  a = n % 4096
  q = n / 4096
  b = q % 4096
  return collatz(a, b, 0, 0, 0, 0)

def collatz(a, b, c, d, e, steps):
  if a == 1:
    if b + c + d + e == 0:
      return steps
    else:
      return advance(a, b, c, d, e, steps)
  else:
    return advance(a, b, c, d, e, steps)

def advance(a, b, c, d, e, steps):
  if a % 2 == 0:
    na = a / 2 + (b % 2) * 2048
    nb = b / 2 + (c % 2) * 2048
    nc = c / 2 + (d % 2) * 2048
    nd = d / 2 + (e % 2) * 2048
    ne = e / 2
    return collatz(na, nb, nc, nd, ne, steps + 1)
  else:
    t0 = 3 * a + 1
    na = t0 % 4096
    carry0 = t0 / 4096
    t1 = 3 * b + carry0
    nb = t1 % 4096
    carry1 = t1 / 4096
    t2 = 3 * c + carry1
    nc = t2 % 4096
    carry2 = t2 / 4096
    t3 = 3 * d + carry2
    nd = t3 % 4096
    carry3 = t3 / 4096
    t4 = 3 * e + carry3
    ne = t4 % 4096
    return collatz(na, nb, nc, nd, ne, steps + 1)
