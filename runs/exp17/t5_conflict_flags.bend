# t5_conflict_flags: the clustering list is read once into an index-keyed tuple-tree that grows as the walk goes
# (MSB-first keys: when i reaches 2^l the tree becomes (tree, zeros), so no length is needed in advance; keyed
# puts pipeline behind the list read). The must-not-link list is read in parallel; every pair reads c[a], c[b]
# and applies a keyed OR (c[a] == c[b]) at key c[a] of a flag tree. The output zips the index tree with the flag
# tree and emits flag[i] for every i with c[i] == i (canonical ids, ascending), tail-threaded.
# ---- base: levels, constant trees, keyed increment, flatten (first n leaves, tail-threaded)
def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def inc(t, k, l, m):
  switch l:
    case 0:
      return t + 1
    case _:
      (a, b) = t
      if k & m:
        return (a, inc(b, k, l-1, m >> 1))
      else:
        return (inc(a, k, l-1, m >> 1), b)

def flat(t, l, base, n, acc):
  switch l:
    case 0:
      if base < n:
        return List/Cons(t, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, n, flat(b, l-1, base + h, n, acc))

def max(a, b):
  return a + (b > a) * (b - a)

def min(a, b):
  return a - (a > b) * (a - b)
def prog(x):
  (cs, mnl) = x
  (n, C, l) = walk(cs, 0, 0, 0, 1)
  m = (1 << l) >> 1
  B = walkm(mnl, C, zt(l), l, m)
  return flags(C, B, l, 0, n, [])

def grow(T, g, l):
  switch g:
    case 0:
      return T
    case _:
      return (T, zt(l))

def put(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, put(b, k, l-1, m >> 1, v))
      else:
        return (put(a, k, l-1, m >> 1, v), b)

def walk(xs, i, T, l, p):
  match xs:
    case List/Nil:
      return (i, T, l)
    case List/Cons:
      g = (i == p) & (i > 0)
      l2 = l + g
      p2 = p << g
      return walk(xs.tail, i + 1, put(grow(T, g, l), i, l2, p2 >> 1, xs.head), l2, p2)

def get(t, k, l, m):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      if k & m:
        return get(b, k, l-1, m >> 1)
      else:
        return get(a, k, l-1, m >> 1)

def setor(t, k, l, m, f):
  switch l:
    case 0:
      return t | f
    case _:
      (a, b) = t
      if k & m:
        return (a, setor(b, k, l-1, m >> 1, f))
      else:
        return (setor(a, k, l-1, m >> 1, f), b)

def walkm(ps, C, B, l, m):
  match ps:
    case List/Nil:
      return B
    case List/Cons:
      (a, b) = ps.head
      ca = get(C, a, l, m)
      cb = get(C, b, l, m)
      return walkm(ps.tail, C, setor(B, ca, l, m, ca == cb), l, m)

def flags(C, B, l, base, n, acc):
  switch l:
    case 0:
      if (base < n) & (C == base):
        return List/Cons(B, acc)
      else:
        return acc
    case _:
      (c1, c2) = C
      (b1, b2) = B
      h = 1 << (l-1)
      return flags(c1, b1, l-1, base, n, flags(c2, b2, l-1, base + h, n, acc))
