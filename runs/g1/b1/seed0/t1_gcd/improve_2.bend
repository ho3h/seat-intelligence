def prog(x):
  (a, b) = x
  return gcd_batch(a, b)

def gcd_batch(a, b):
  if b == 0:
    return a
  else:
    r = a % b
    if r == 0:
      return b
    else:
      s = b % r
      if s == 0:
        return r
      else:
        t = r % s
        if t == 0:
          return s
        else:
          u = s % t
          if u == 0:
            return t
          else:
            return gcd_batch(t, u)
