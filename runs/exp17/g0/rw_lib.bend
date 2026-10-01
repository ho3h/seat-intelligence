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
