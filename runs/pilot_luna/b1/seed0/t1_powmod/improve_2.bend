def prog(x):
  (base, exp, m) = x
  b = base % m
  b2 = (b * b) % m
  b3 = (b2 * b) % m
  b4 = (b2 * b2) % m
  b8 = (b4 * b4) % m
  b12 = (b8 * b4) % m
  return pow16(b, b2, b3, b4, b8, b12, exp, m)

def pow16(b, b2, b3, b4, b8, b12, e, m):
  if e == 0:
    return 1 % m
  else:
    p = pow16(b, b2, b3, b4, b8, b12, e / 16, m)
    p2 = (p * p) % m
    p4 = (p2 * p2) % m
    p8 = (p4 * p4) % m
    p16 = (p8 * p8) % m
    r = e % 16
    lo = choose4(1 % m, b, b2, b3, r % 4)
    hi = choose4(1 % m, b4, b8, b12, r / 4)
    return (p16 * lo * hi) % m

def choose4(one, p1, p2, p3, d):
  if d == 0:
    return one
  else:
    if d == 1:
      return p1
    else:
      if d == 2:
        return p2
      else:
        return p3
