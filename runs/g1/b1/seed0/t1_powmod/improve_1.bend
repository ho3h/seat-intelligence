def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    base2 = (base * base) % m
    base4 = (base2 * base2) % m
    exp4 = exp / 4
    digit = exp % 4
    if digit == 0:
      return powmod(base4, exp4, m, acc)
    else:
      if digit == 1:
        acc1 = (acc * base) % m
        return powmod(base4, exp4, m, acc1)
      else:
        if digit == 2:
          acc1 = (acc * base2) % m
          return powmod(base4, exp4, m, acc1)
        else:
          acc1 = (acc * base) % m
          acc2 = (acc1 * base2) % m
          return powmod(base4, exp4, m, acc2)
