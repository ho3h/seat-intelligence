def prog(x):
  (a, b) = x
  return gcd_bin(a, b, 1)

def gcd_bin(a, b, scale):
  if a == 0:
    return b * scale
  else:
    if b == 0:
      return a * scale
    else:
      if (a & 1) == 0:
        if (b & 1) == 0:
          return gcd_bin(a >> 1, b >> 1, scale * 2)
        else:
          return gcd_bin(a >> 1, b, scale)
      else:
        if (b & 1) == 0:
          return gcd_bin(a, b >> 1, scale)
        else:
          if a >= b:
            return gcd_bin((a - b) >> 1, b, scale)
          else:
            return gcd_bin(a, (b - a) >> 1, scale)
