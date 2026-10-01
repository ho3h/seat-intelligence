def prog(n):
  if n >= 28:
    return 0
  else:
    return lookup(n)

def lookup(n):
  if n < 14:
    return lookup_low(n)
  else:
    return lookup_high(n)

def lookup_low(n):
  if n < 7:
    return lookup_low7(n)
  else:
    return lookup_low14(n)

def lookup_low7(n):
  if n < 3:
    if n < 1:
      return 1
    else:
      if n < 2:
        return 1
      else:
        return 2
  else:
    if n < 5:
      if n < 4:
        return 6
      else:
        return 24
    else:
      if n < 6:
        return 120
      else:
        return 720

def lookup_low14(n):
  if n < 10:
    if n < 8:
      return 5040
    else:
      if n < 9:
        return 40320
      else:
        return 362880
  else:
    if n < 12:
      if n < 11:
        return 3628800
      else:
        return 6362368
    else:
      if n < 13:
        return 9239552
      else:
        return 2673664

def lookup_high(n):
  if n < 21:
    return lookup_high21(n)
  else:
    return lookup_high28(n)

def lookup_high21(n):
  if n < 17:
    if n < 15:
      return 3876864
    else:
      if n < 16:
        return 7821312
      else:
        return 7700480
  else:
    if n < 19:
      if n < 18:
        return 13467648
      else:
        return 7536640
    else:
      if n < 20:
        return 8978432
      else:
        return 11796480

def lookup_high28(n):
  if n < 24:
    if n < 22:
      return 12845056
    else:
      if n < 23:
        return 14155776
      else:
        return 6815744
  else:
    if n < 26:
      return 12582912
    else:
      return 8388608
