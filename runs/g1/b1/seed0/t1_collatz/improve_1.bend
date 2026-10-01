def prog(n):
  base = 4194304
  a = n % base
  b = n / base
  return collatz(a, b, 0, 0, 0)

def collatz(a, b, c, d, steps):
  if a == 1:
    if b == 0:
      if c == 0:
        if d == 0:
          return steps
        else:
          return advance(a, b, c, d, steps)
      else:
        return advance(a, b, c, d, steps)
    else:
      return advance(a, b, c, d, steps)
  else:
    return advance(a, b, c, d, steps)

def advance(a, b, c, d, steps):
  base = 4194304
  half = 2097152
  if a % 2 == 0:
    na = a / 2 + (b % 2) * half
    nb = b / 2 + (c % 2) * half
    nc = c / 2 + (d % 2) * half
    nd = d / 2
    return collatz(na, nb, nc, nd, steps + 1)
  else:
    t0 = 3 * a + 1
    l0 = t0 % base
    k0 = t0 / base
    t1 = 3 * b + k0
    l1 = t1 % base
    k1 = t1 / base
    t2 = 3 * c + k1
    l2 = t2 % base
    k2 = t2 / base
    t3 = 3 * d + k2
    l3 = t3 % base
    na = l0 / 2 + (l1 % 2) * half
    nb = l1 / 2 + (l2 % 2) * half
    nc = l2 / 2 + (l3 % 2) * half
    nd = l3 / 2
    return collatz(na, nb, nc, nd, steps + 2)
