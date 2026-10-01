def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    if exp % 2 == 1:
      acc2 = (acc * base) % m
    else:
      acc2 = acc
    base2 = (base * base) % m
    exp2 = exp / 2
    return powmod(base2, exp2, m, acc2)
