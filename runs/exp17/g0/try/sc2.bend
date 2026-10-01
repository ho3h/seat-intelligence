# t5_rewrite_sameas_cycle: pointer jumping with a fixed number of rounds (l = ceil(log2 n), no convergence test,
# so rounds pipeline). A round is Q'[i] = Q[Q[i]] for all i at once, by return addresses: leaf i of the new
# tree is an unscoped-lambda variable whose sink is pushed at leaf Q[i] of a request tree; then every old
# value is wired into its sinks (keyed pushes collapse level by level; delivery walks the sink list). After l rounds
# every node of an acyclic chain points at its root, while nodes that reach a cycle point at cycle nodes, which
# are not roots. Answer = some i < n whose Q[i] is not a root (p[j] == j), by one more gather.
def prog(p):
  n = len(p)
  (l, m) = lvl(n, 0, 1)
  P = cwalk(p, 0, zt(l), l, m)
  (Q, z) = rounds(P, l, l, m)
  R = rflags(P, l, 0)
  return z + anyb(gall(R, Q, l, l, m), l, 0, n)

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

# G[i] = T[Q[i]]
def gall(T, Q, lv, l, m):
  switch lv:
    case 0:
      return get(T, Q, l, m)
    case _:
      (q1, q2) = Q
      return (gall(T, q1, lv-1, l, m), gall(T, q2, lv-1, l, m))

# one jump: leaf i of the new tree is $r (arrives later), and a sink for it goes to leaf Q[i] of R;
# then every old Q value is wired into the sinks at its leaf.
def step(Q, lv, l, m, R):
  switch lv:
    case 0:
      return ($r, push(R, Q, l, m, lambda $r: 0))
    case _:
      (q1, q2) = Q
      (a, R1) = step(q1, lv-1, l, m, R)
      (b, R2) = step(q2, lv-1, l, m, R1)
      return ((a, b), R2)

def rounds(Q, k, l, m):
  switch k:
    case 0:
      return (Q, 0)
    case _:
      (Q2, R) = step(Q, l, l, m, zl(l))
      z = deliver_all(Q, R, l)
      (Q3, z2) = rounds(Q2, k-1, l, m)
      return (Q3, z + z2)

def rflags(P, l, base):
  switch l:
    case 0:
      return P == base
    case _:
      (a, b) = P
      h = 1 << (l-1)
      return (rflags(a, l-1, base), rflags(b, l-1, base + h))

def anyb(F, l, base, n):
  switch l:
    case 0:
      return (F == 0) & (base < n)
    case _:
      (a, b) = F
      h = 1 << (l-1)
      return anyb(a, l-1, base, n) | anyb(b, l-1, base + h, n)

def seq(z, v):
  switch z:
    case 0:
      return v
    case _:
      return v

def len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len(xs.tail)

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def top(L):
  switch L:
    case 0:
      return 0
    case _:
      return 1 << L-1

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def zl(l):
  switch l:
    case 0:
      return []
    case _:
      return (zl(l-1), zl(l-1))

def set(t, k, l, m, v):
  switch l:
    case 0:
      return v
    case _:
      (a, b) = t
      if k & m:
        return (a, set(b, k, l-1, m >> 1, v))
      else:
        return (set(a, k, l-1, m >> 1, v), b)

def setb(t, k, l, m, bit):
  switch l:
    case 0:
      return t | bit
    case _:
      (a, b) = t
      if k & m:
        return (a, setb(b, k, l-1, m >> 1, bit))
      else:
        return (setb(a, k, l-1, m >> 1, bit), b)

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

# c list -> tree keyed by position (keyed sets collapse level by level under the walk)
def cwalk(xs, i, C, l, m):
  match xs:
    case List/Nil:
      return C
    case List/Cons:
      return cwalk(xs.tail, i + 1, set(C, i, l, m, xs.head), l, m)

def deliver_all(C, Q, l):
  switch l:
    case 0:
      return deliver(C, Q)
    case _:
      (c1, c2) = C
      (q1, q2) = Q
      return deliver_all(c1, q1, l-1) + deliver_all(c2, q2, l-1)

def deliver(v, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(v) + deliver(v, sinks.tail)

def popc(x):
  a = x - ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b + (b >> 4)) & 3855
  return (c + (c >> 8)) & 31

def pcount(t, l):
  switch l:
    case 0:
      return popc(t)
    case _:
      (a, b) = t
      return pcount(a, l-1) + pcount(b, l-1)
