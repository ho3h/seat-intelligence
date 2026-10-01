# t5_cluster_implied_unproposed: closure pairs = sum over clusters of s(s-1)/2, from max labels by a stream
# dataflow (see ccs) and a block-threaded keyed histogram of labels. Distinct input pairs:
# a trie of 16-bit words keyed by (u, v >> 4), each pair ORs one bit in during the list walk (keyed updates
# collapse level by level), then a popcount reduction.
#include base
#include ccs
#include scatkv
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (l2, m2) = lvl((n + 15) >> 4, 0, 1)
  W = walkw(es, zt(l + l2, 0), l, m, l2, m << l2)
  (D, z) = ccs(es, l, m, 1, 16777215)
  C = scatkv(kv(D, l, 0, n), l, l, m)
  return z + pairs(C, l) - pops(W, l + l2)

def kv(D, l, base, n):
  switch l:
    case 0:
      return (D, base < n)
    case _:
      (a, b) = D
      h = 1 << (l-1)
      return (kv(a, l-1, base, n), kv(b, l-1, base + h, n))

def orb(t, k, l, m, b):
  switch l:
    case 0:
      return t | b
    case _:
      (a, c) = t
      if k & m:
        return (a, orb(c, k, l-1, m >> 1, b))
      else:
        return (orb(a, k, l-1, m >> 1, b), c)

def walkw(es, W, l, m, l2, mw):
  match es:
    case List/Nil:
      return W
    case List/Cons:
      (u, v) = es.head
      W2 = orb(W, (u << l2) | (v >> 4), l + l2, mw, 1 << (v & 15))
      return walkw(es.tail, W2, l, m, l2, mw)

def pairs(t, l):
  switch l:
    case 0:
      return (t * (t - 1)) / 2
    case _:
      (a, b) = t
      return pairs(a, l-1) + pairs(b, l-1)

def pop16(x):
  a = (x & 21845) + ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b & 3855) + ((b >> 4) & 3855)
  return (c & 255) + (c >> 8)

def pops(t, l):
  switch l:
    case 0:
      return pop16(t)
    case _:
      (a, b) = t
      return pops(a, l-1) + pops(b, l-1)
