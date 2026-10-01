def prog(x):
  (base, exp, m) = x
  return powmod256(base % m, exp, m, 1 % m)

def powmod256(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    base2 = (base * base) % m
    base4 = (base2 * base2) % m
    base8 = (base4 * base4) % m
    base16 = (base8 * base8) % m
    base32 = (base16 * base16) % m
    base64 = (base32 * base32) % m
    base128 = (base64 * base64) % m
    base256 = (base128 * base128) % m

    digit = exp % 256

    if digit % 2 == 1:
      acc1 = (acc * base) % m
    else:
      acc1 = acc
    if (digit / 2) % 2 == 1:
      acc2 = (acc1 * base2) % m
    else:
      acc2 = acc1
    if (digit / 4) % 2 == 1:
      acc3 = (acc2 * base4) % m
    else:
      acc3 = acc2
    if (digit / 8) % 2 == 1:
      acc4 = (acc3 * base8) % m
    else:
      acc4 = acc3
    if (digit / 16) % 2 == 1:
      acc5 = (acc4 * base16) % m
    else:
      acc5 = acc4
    if (digit / 32) % 2 == 1:
      acc6 = (acc5 * base32) % m
    else:
      acc6 = acc5
    if (digit / 64) % 2 == 1:
      acc7 = (acc6 * base64) % m
    else:
      acc7 = acc6
    if (digit / 128) % 2 == 1:
      acc8 = (acc7 * base128) % m
    else:
      acc8 = acc7

    return powmod256(base256, exp / 256, m, acc8)
