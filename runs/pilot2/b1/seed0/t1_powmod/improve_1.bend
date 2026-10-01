def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    digit = exp % 16

    base2 = (base * base) % m
    base4 = (base2 * base2) % m
    base8 = (base4 * base4) % m
    base16 = (base8 * base8) % m

    if digit % 2 == 1:
      acc1 = (acc * base) % m
    else:
      acc1 = acc

    if digit / 2 % 2 == 1:
      acc2 = (acc1 * base2) % m
    else:
      acc2 = acc1

    if digit / 4 % 2 == 1:
      acc3 = (acc2 * base4) % m
    else:
      acc3 = acc2

    if digit / 8 == 1:
      acc4 = (acc3 * base8) % m
    else:
      acc4 = acc3

    return powmod(base16, exp / 16, m, acc4)
