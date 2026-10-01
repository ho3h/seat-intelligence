# ---- scatkv: trie whose leaves are (key, x) -> trie C with C[key] = sum of x (x = 0 means nothing).
# Blocks of 8 leaves thread their keyed adds through a private zero trie; blocks are added pointwise.
def addt(a, b, l):
  switch l:
    case 0:
      return a + b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (addt(a1, b1, l-1), addt(a2, b2, l-1))

def addk(t, k, l, m, x):
  switch l:
    case 0:
      return t + x
    case _:
      (a, b) = t
      if k & m:
        return (a, addk(b, k, l-1, m >> 1, x))
      else:
        return (addk(a, k, l-1, m >> 1, x), b)

def skvt(KV, lv, l, m, C):
  switch lv:
    case 0:
      (k, x) = KV
      return addk(C, k, l, m, x)
    case _:
      (a, b) = KV
      return skvt(b, lv-1, l, m, skvt(a, lv-1, l, m, C))

def scatkv(KV, lv, l, m):
  if lv <= 3:
    return skvt(KV, lv, l, m, zt(l, 0))
  else:
    (a, b) = KV
    return addt(scatkv(a, lv - 1, l, m), scatkv(b, lv - 1, l, m), l)
