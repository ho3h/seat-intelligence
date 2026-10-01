# t5_metric_purity: the two label lists are read in parallel into index-keyed tuple-trees (lib/growtree), zipped
# leafwise. Then two all-pairs passes, O(n^2) work and O(levels) depth, using only label equality (no assumption on
# the label values):
#   c_i = #{j : pred_j == pred_i and truth_j == truth_i}  (the size of i's (pred, truth) class)
#   i is its pred group's representative iff no j in the group has c_j > c_i, or c_j == c_i and j < i;
# purity = sum of c_i over representatives.
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
# ---- growtree: read a list into an index-keyed tuple-tree without knowing its length: MSB-first keys, and when
# i reaches 2^l the tree becomes (tree, zeros). Keyed puts pipeline behind the list read. -> (n, tree, depth)
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

def gwalk(xs, i, T, l, p):
  match xs:
    case List/Nil:
      return (i, T, l)
    case List/Cons:
      g = (i == p) & (i > 0)
      l2 = l + g
      p2 = p << g
      return gwalk(xs.tail, i + 1, put(grow(T, g, l), i, l2, p2 >> 1, xs.head), l2, p2)
def prog(x):
  (pr, tr) = x
  (n, P, l) = gwalk(pr, 0, 0, 0, 1)
  (n2, Q, l2) = gwalk(tr, 0, 0, 0, 1)
  Z = zipq(P, Q, l, 0, n)
  C = cnts(Z, Z, l, l, 0, n)
  return reps(C, C, l, l, 0)

# leaf: (valid, p, t)
def zipq(P, Q, l, base, n):
  switch l:
    case 0:
      return (base < n, P, Q)
    case _:
      (p1, p2) = P
      (q1, q2) = Q
      h = 1 << (l-1)
      return (zipq(p1, q1, l-1, base, n), zipq(p2, q2, l-1, base + h, n))

# leaf: (valid, i, p, c)
def cnts(T, A, l, L, base, n):
  switch l:
    case 0:
      (v, p, t) = T
      return (v, base, p, v * same(A, L, p, t))
    case _:
      (a, b) = T
      h = 1 << (l-1)
      return (cnts(a, A, l-1, L, base, n), cnts(b, A, l-1, L, base + h, n))

def same(A, l, p, t):
  switch l:
    case 0:
      (v, q, u) = A
      return v & (q == p) & (u == t)
    case _:
      (a, b) = A
      return same(a, l-1, p, t) + same(b, l-1, p, t)

def reps(C, A, l, L, acc):
  switch l:
    case 0:
      (v, i, p, c) = C
      return v * (beats(A, L, i, p, c) == 0) * c
    case _:
      (a, b) = C
      return reps(a, A, l-1, L, 0) + reps(b, A, l-1, L, 0)

# number of j in i's pred group that beat i: larger c, or equal c and smaller index
def beats(A, l, i, p, c):
  switch l:
    case 0:
      (v, j, q, d) = A
      return v * (q == p) * ((d > c) + (d == c) * (j < i))
    case _:
      (a, b) = A
      return beats(a, l-1, i, p, c) + beats(b, l-1, i, p, c)
