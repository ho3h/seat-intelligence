# ---- bits: exact bitsets as balanced tuple-trees of 24-bit words (depth wl covers 24 * 2^wl bits)
def bzero(wl):
  switch wl:
    case 0:
      return 0
    case _:
      return (bzero(wl-1), bzero(wl-1))

def bit(i, wl):
  switch wl:
    case 0:
      return 1 << i
    case _:
      h = 24 << (wl-1)
      if i < h:
        return (bit(i, wl-1), bzero(wl-1))
      else:
        return (bzero(wl-1), bit(i - h, wl-1))

def bxor(a, b, wl):
  switch wl:
    case 0:
      return a ^ b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (bxor(a1, b1, wl-1), bxor(a2, b2, wl-1))

def beq(a, b, wl):
  switch wl:
    case 0:
      return a == b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return beq(a1, b1, wl-1) & beq(a2, b2, wl-1)

def bor(a, b, wl):
  switch wl:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (bor(a1, b1, wl-1), bor(a2, b2, wl-1))

def pop24(x):
  x1 = x - ((x >> 1) & 5592405)
  x2 = (x1 & 3355443) + ((x1 >> 2) & 3355443)
  x3 = (x2 + (x2 >> 4)) & 986895
  return (x3 * 65793) >> 16

def bpop(a, wl):
  switch wl:
    case 0:
      return pop24(a)
    case _:
      (a1, a2) = a
      return bpop(a1, wl-1) + bpop(a2, wl-1)
