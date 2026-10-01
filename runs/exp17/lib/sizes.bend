# ---- sizes: component sizes from a final label tree F (label = a member id, padding = 16777215).
# size(r) = number of leaves labelled r: every root position r counts over a copy of F (O(n^2) work, O(L) depth).
def cnt_eq(F, l, r):
  switch l:
    case 0:
      return F == r
    case _:
      (a, b) = F
      return cnt_eq(a, l-1, r) + cnt_eq(b, l-1, r)

# tree of sizes at root positions (0 elsewhere); key(r) = the label a root r carries
def root_sizes(T, F, L, l, base, n, key):
  switch l:
    case 0:
      if base < n:
        if T == key(base):
          return cnt_eq(F, L, T)
        else:
          return 0
      else:
        return 0
    case _:
      (a, b) = T
      h = 1 << (l-1)
      return (root_sizes(a, F, L, l-1, base, n, key), root_sizes(b, F, L, l-1, base + h, n, key))

def tmax(t, l):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      return max(tmax(a, l-1), tmax(b, l-1))

def tpairs(t, l):
  switch l:
    case 0:
      return (t * (t - (t > 0))) / 2
    case _:
      (a, b) = t
      return tpairs(a, l-1) + tpairs(b, l-1)

# scatter-count: chain of keyed increments threaded through the label tree (padding leaves skipped)
def scat(F, l, L, m, base, n, C):
  switch l:
    case 0:
      if base < n:
        return inc(C, F, L, m)
      else:
        return C
    case _:
      (a, b) = F
      h = 1 << (l-1)
      return scat(b, l-1, L, m, base + h, n, scat(a, l-1, L, m, base, n, C))
