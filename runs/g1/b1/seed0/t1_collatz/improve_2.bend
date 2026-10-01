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
  if a % 2 == 0:
    if a % 8 == 0:
      if a % 16 == 0:
        if a % 32 == 0:
          na = a / 32 + (b % 32) * 131072
          nb = b / 32 + (c % 32) * 131072
          nc = c / 32 + (d % 32) * 131072
          nd = d / 32
          return collatz(na, nb, nc, nd, steps + 5)
        else:
          na = a / 16 + (b % 16) * 262144
          nb = b / 16 + (c % 16) * 262144
          nc = c / 16 + (d % 16) * 262144
          nd = d / 16
          return collatz(na, nb, nc, nd, steps + 4)
      else:
        na = a / 8 + (b % 8) * 524288
        nb = b / 8 + (c % 8) * 524288
        nc = c / 8 + (d % 8) * 524288
        nd = d / 8
        return collatz(na, nb, nc, nd, steps + 3)
    else:
      if a % 4 == 0:
        na = a / 4 + (b % 4) * 1048576
        nb = b / 4 + (c % 4) * 1048576
        nc = c / 4 + (d % 4) * 1048576
        nd = d / 4
        return collatz(na, nb, nc, nd, steps + 2)
      else:
        na = a / 2 + (b % 2) * 2097152
        nb = b / 2 + (c % 2) * 2097152
        nc = c / 2 + (d % 2) * 2097152
        nd = d / 2
        return collatz(na, nb, nc, nd, steps + 1)
  else:
    t0 = 3 * a + 1
    l0 = t0 % 4194304
    k0 = t0 / 4194304
    t1 = 3 * b + k0
    l1 = t1 % 4194304
    k1 = t1 / 4194304
    t2 = 3 * c + k1
    l2 = t2 % 4194304
    k2 = t2 / 4194304
    t3 = 3 * d + k2
    l3 = t3 % 4194304
    na = l0 / 2 + (l1 % 2) * 2097152
    nb = l1 / 2 + (l2 % 2) * 2097152
    nc = l2 / 2 + (l3 % 2) * 2097152
    nd = l3 / 2
    return collatz(na, nb, nc, nd, steps + 2)
