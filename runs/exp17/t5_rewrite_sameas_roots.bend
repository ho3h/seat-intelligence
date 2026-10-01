# t5_rewrite_sameas_roots: the pointer chase as a dataflow net (no rounds). Walking p, node i pushes a
# "return address" sink (unscoped lambda) into a Braun tree at leaf p[i] of a request tree and outputs
# root(i) = i if p[i] == i else $r (the value that will arrive in its sink). Then every node's own output
# value is wired into the sinks at its leaf (a balanced Braun delivery, log(in-degree) deep), so roots
# ripple down the pointer forest as soon as they exist. Acyclicity (precondition) means no wire waits on itself.
type Br:
  Node { e, l, r }
  Leaf

def prog(p):
  n = len(p)
  (l, m) = lvl(n, 0, 1)
  (out, Q, V) = walk(p, 0, zb(l), zt(l), l, m)
  return seq(dall(V, Q, l), out)

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

def pick(c, a, b):
  switch c:
    case 0:
      return b
    case _:
      return a

def walk(xs, i, Q, V, l, m):
  match xs:
    case List/Nil:
      return ([], Q, V)
    case List/Cons:
      t = xs.head
      v = pick(t == i, i, $r)
      (rest, Q2, V2) = walk(xs.tail, i + 1, pushb(Q, t, l, m, lambda $r: 0), set(V, i, l, m, v), l, m)
      return (List/Cons(v, rest), Q2, V2)

def dall(V, Q, l):
  switch l:
    case 0:
      return dl(V, Q)
    case _:
      (v1, v2) = V
      (q1, q2) = Q
      return dall(v1, q1, l-1) + dall(v2, q2, l-1)

def dl(v, t):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = t.e
      return f(v) + dl(v, t.l) + dl(v, t.r)

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
