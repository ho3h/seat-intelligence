def prog(x):
  (base, exp, m) = x
  b = base % m
  b2 = (b * b) % m
  b3 = (b2 * b) % m
  return pow4(b, b2, b3, exp, m)

def pow4(b, b2, b3, e, m):
  if e == 0:
    return 1 % m
  else:
    p = pow4(b, b2, b3, e / 4, m)
    p2 = (p * p) % m
    p4 = (p2 * p2) % m
    r = e % 4
    if r == 0:
      return p4
    else:
      if r == 1:
        return (p4 * b) % m
      else:
        if r == 2:
          return (p4 * b2) % m
        else:
          return (p4 * b3) % m
