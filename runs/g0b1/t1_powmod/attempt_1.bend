def prog(x):
  (b, e, m) = x
  return pm(b % m, e, m, 1 % m)

def pm(b, e, m, acc):
  if e == 0:
    return acc
  else:
    if (e & 1) == 1:
      return pm((b * b) % m, e >> 1, m, (acc * b) % m)
    else:
      return pm((b * b) % m, e >> 1, m, acc)
