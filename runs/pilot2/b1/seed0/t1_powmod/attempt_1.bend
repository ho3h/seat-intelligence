def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    if exp % 2 == 1:
      next_acc = (acc * base) % m
    else:
      next_acc = acc
    next_base = (base * base) % m
    return powmod(next_base, exp / 2, m, next_acc)
