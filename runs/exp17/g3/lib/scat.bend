# ---- scat: histogram of the labels of D (leaf (label, flag)) into a count trie keyed by label.
# Blocks of 8 consecutive vertices thread their keyed increments through a private zero trie; block tries are
# added pointwise in a balanced tree, so no thread is longer than 8 updates.
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

def scatt(D, lv, base, n, l, m, C):
  switch lv:
    case 0:
      (d, f) = D
      return addk(C, d, l, m, base < n)
    case _:
      (a, b) = D
      h = 1 << (lv-1)
      return scatt(b, lv-1, base + h, n, l, m, scatt(a, lv-1, base, n, l, m, C))

def scat(D, lv, base, n, l, m):
  if lv <= 3:
    return scatt(D, lv, base, n, l, m, zt(l, 0))
  else:
    (a, b) = D
    h = 1 << (lv - 1)
    return addt(scat(a, lv - 1, base, n, l, m), scat(b, lv - 1, base + h, n, l, m), l)
