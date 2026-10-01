# t5_decide_stage_cap: bucket sort. The walk pushes each triple into a trie keyed by 1000 - score (rejected
# ones into a junk bucket 1023; branch-free key, so the walk never waits); keyed pushes collapse level by
# level. Each real bucket sorts its few pairs by (u, v) (insertion sort, all buckets in parallel), an exclusive
# prefix sum over bucket sizes gives every bucket its first position, and the output is the trie flattened
# (tail-threaded, so the conses are built in parallel) keeping positions < cap.
# ---- base: tuple tries keyed by vertex id (MSB first), l levels, m = top-bit mask
type Br:
  Node { e, l, r }
  Leaf

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l, z):
  switch l:
    case 0:
      return z
    case _:
      return (zt(l-1, z), zt(l-1, z))

def zb(l):
  switch l:
    case 0:
      return Br/Leaf
    case _:
      return (zb(l-1), zb(l-1))

def bins(t, e):
  match t:
    case Br/Leaf:
      return Br/Node(e, Br/Leaf, Br/Leaf)
    case Br/Node:
      return Br/Node(e, bins(t.r, t.e), t.l)

def pushb(t, k, l, m, e):
  switch l:
    case 0:
      return bins(t, e)
    case _:
      (a, b) = t
      if k & m:
        return (a, pushb(b, k, l-1, m >> 1, e))
      else:
        return (pushb(a, k, l-1, m >> 1, e), b)

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

def updmin(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmin(b, k, l-1, m >> 1, x))
      else:
        return (updmin(a, k, l-1, m >> 1, x), b)

def updmax(t, k, l, m, x):
  switch l:
    case 0:
      return t + (x > t) * (x - t)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmax(b, k, l-1, m >> 1, x))
      else:
        return (updmax(a, k, l-1, m >> 1, x), b)
def prog(x):
  (tau, cap, cs) = x
  B = walk(cs, tau, zt(10, []))
  S = sortb(B, 10, 0)
  (P, tot) = pref(S, 10, 0, 0)
  d = tot - cap
  return (flat(P, 10, cap, []), (tot > cap) * d)

def push(t, k, l, m, v):
  switch l:
    case 0:
      return List/Cons(v, t)
    case _:
      (a, b) = t
      if k & m:
        return (a, push(b, k, l-1, m >> 1, v))
      else:
        return (push(a, k, l-1, m >> 1, v), b)

def walk(cs, tau, B):
  match cs:
    case List/Nil:
      return B
    case List/Cons:
      (u, v, s) = cs.head
      a = s >= tau
      k = 1000 - s
      return walk(cs.tail, tau, push(B, k + (1 - a) * (1023 - k), 10, 512, (u, v)))

def before(p, q):
  (u1, v1) = p
  (u2, v2) = q
  return (u1 < u2) | ((u1 == u2) & (v1 < v2))

def ins(xs, e):
  match xs:
    case List/Nil:
      return [e]
    case List/Cons:
      if before(xs.head, e):
        return List/Cons(xs.head, ins(xs.tail, e))
      else:
        return List/Cons(e, xs)

def isort(xs, acc, c):
  match xs:
    case List/Nil:
      return (acc, c)
    case List/Cons:
      return isort(xs.tail, ins(acc, xs.head), c + 1)

def sortb(B, l, idx):
  switch l:
    case 0:
      if idx == 1023:
        return ([], 0)
      else:
        return isort(B, [], 0)
    case _:
      (a, b) = B
      h = 1 << (l-1)
      return (sortb(a, l-1, idx), sortb(b, l-1, idx + h))

# leaves become (sorted list, first position); returns the total
def pref(S, l, idx, off):
  switch l:
    case 0:
      (xs, c) = S
      return ((xs, off), c)
    case _:
      (a, b) = S
      h = 1 << (l-1)
      (a2, ca) = pref(a, l-1, idx, off)
      (b2, cb) = pref(b, l-1, idx + h, off + ca)
      return ((a2, b2), ca + cb)

def take(xs, p, cap, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if p < cap:
        return List/Cons(xs.head, take(xs.tail, p + 1, cap, acc))
      else:
        return acc

def flat(P, l, cap, acc):
  switch l:
    case 0:
      (xs, p) = P
      return take(xs, p, cap, acc)
    case _:
      (a, b) = P
      return flat(a, l-1, cap, flat(b, l-1, cap, acc))
