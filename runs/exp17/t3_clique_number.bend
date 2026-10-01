# t3_clique_number: parallel forward-clique enumeration. Forward rows N+(u) = {v > u adjacent} are 16-bit
# word bitsets in one tuple trie keyed by (u, word), set with keyed ORs during the walk. Each vertex x gets
# the list of its forward neighbours WITH their rows through return addresses (unscoped lambdas): the walk
# pushes a sink into y's request list and the wire $r into x's list; at the end every row is wired into its
# sinks. A branch with candidate set P and candidate list C tries every y in C that is in P, recursing on
# (P & N+(y), the members of C left in it); all branches run in parallel, answers max-reduced.
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
  (n, es) = x
  if n == 0:
    return 0
  else:
    (l, m) = lvl(n, 0, 1)
    (lw, mw) = lvl((n + 15) >> 4, 0, 1)
    L = l + lw
    (R, Q, F) = walk(es, zt(L, 0), zt(l, []), zt(l, []), l, m, lw, L, m << lw)
    z = deliver_all(R, Q, l)
    return z + top(R, F, l, lw, mw, 0, n)

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

def walk(es, R, Q, F, l, m, lw, L, M):
  match es:
    case List/Nil:
      return (R, Q, F)
    case List/Cons:
      (p, q) = es.head
      a = p - (p > q) * (p - q)
      b = p + q - a
      R2 = orb(R, (a << lw) | (b >> 4), L, M, 1 << (b & 15))
      Q2 = push(Q, b, l, m, lambda $r: 0)
      F2 = push(F, a, l, m, (b, $r))
      return walk(es.tail, R2, Q2, F2, l, m, lw, L, M)

def deliver_all(R, Q, l):
  switch l:
    case 0:
      return deliver(R, Q)
    case _:
      (r1, r2) = R
      (q1, q2) = Q
      return deliver_all(r1, q1, l-1) + deliver_all(r2, q2, l-1)

def deliver(row, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(row) + deliver(row, sinks.tail)

def andr(a, b, lw):
  switch lw:
    case 0:
      return a & b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (andr(a1, b1, lw-1), andr(a2, b2, lw-1))

def tst(P, y, lw, mw):
  return (get(P, y >> 4, lw, mw) >> (y & 15)) & 1

def mx(a, b):
  return a + (b > a) * (b - a)

def filt(C, P, lw, mw):
  match C:
    case List/Nil:
      return []
    case List/Cons:
      (y, ry) = C.head
      r = filt(C.tail, P, lw, mw)
      if tst(P, y, lw, mw):
        return List/Cons((y, ry), r)
      else:
        return r

# largest clique extendable from candidate set P using candidates C (all members of C are in P)
def ext(C, P, Ca, lw, mw):
  match C:
    case List/Nil:
      return 0
    case List/Cons:
      (y, ry) = C.head
      r = ext(C.tail, P, Ca, lw, mw)
      P2 = andr(P, ry, lw)
      return mx(r, 1 + ext2(filt(Ca, P2, lw, mw), P2, lw, mw))

def ext2(C, P, lw, mw):
  match C:
    case List/Nil:
      return 0
    case List/Cons:
      return ext(C, P, C, lw, mw)

def top(R, F, lv, lw, mw, x, n):
  switch lv:
    case 0:
      if x < n:
        return 1 + ext2(F, R, lw, mw)
      else:
        return 0
    case _:
      (r1, r2) = R
      (f1, f2) = F
      h = 1 << (lv-1)
      return mx(top(r1, f1, lv-1, lw, mw, x, n), top(r2, f2, lv-1, lw, mw, x + h, n))
