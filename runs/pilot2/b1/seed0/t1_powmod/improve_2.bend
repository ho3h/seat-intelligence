def prog(x):
  (base, exp, m) = x
  return powmod(base % m, exp, m, 1 % m)

def powmod(base, exp, m, acc):
  if exp == 0:
    return acc
  else:
    digit = exp % 256
    identity = 1 % m

    b0 = digit % 2
    b1 = digit / 2 % 2
    b2 = digit / 4 % 2
    b3 = digit / 8 % 2
    b4 = digit / 16 % 2
    b5 = digit / 32 % 2
    b6 = digit / 64 % 2
    b7 = digit / 128 % 2

    base2 = (base * base) % m
    base4 = (base2 * base2) % m
    base8 = (base4 * base4) % m
    base16 = (base8 * base8) % m
    base32 = (base16 * base16) % m
    base64 = (base32 * base32) % m
    base128 = (base64 * base64) % m
    base256 = (base128 * base128) % m

    (p01, a01) = merge(base, b0, base2, b1, identity, m)
    (p23, a23) = merge(base4, b2, base8, b3, identity, m)
    (p45, a45) = merge(base16, b4, base32, b5, identity, m)
    (p67, a67) = merge(base64, b6, base128, b7, identity, m)

    (p03, a03) = merge(p01, a01, p23, a23, identity, m)
    (p47, a47) = merge(p45, a45, p67, a67, identity, m)
    (factor, active) = merge(p03, a03, p47, a47, identity, m)

    if active == 1:
      next_acc = (acc * factor) % m
    else:
      next_acc = acc

    return powmod(base256, exp / 256, m, next_acc)

def merge(a, active_a, b, active_b, identity, m):
  if active_a == 1:
    if active_b == 1:
      return ((a * b) % m, 1)
    else:
      return (a, 1)
  else:
    if active_b == 1:
      return (b, 1)
    else:
      return (identity, 0)
