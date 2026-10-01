def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(b, e, m, a):
  if e == 0:
    return a
  else:
    if e % 2 == 1:
      return powmod((b * b) % m, e / 2, m, (a * b) % m)
    else:
      return powmod((b * b) % m, e / 2, m, a)
