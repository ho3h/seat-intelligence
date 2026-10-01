# t3_triangle_count: adjacency bitsets as ONE tuple-tree keyed by (u, word of v) (16-bit words, MSB first).
# Each edge sets two bits with keyed updates (they collapse level by level). Rows reach the edge queries
# through "return addresses": for each edge the walk creates two unscoped lambdas (wires) and pushes
# them into a sink tree at leaves u and v; at the end every row is wired into its sinks. The per-edge
# answer popcount(row_u AND row_v) is added into a sum tree keyed by u. Answer = total / 3.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (lw, mw) = lvl((n + 15) / 16, 0, 1)
  L = l + lw
  M = top(L)
  (R, Q, S) = walk(es, zt(L), zl(l), zt(l), l, m, lw, L, M)
  return (total(S, l) + deliver_all(R, Q, l, lw)) / 3

def top(L):
  switch L:
    case 0:
      return 0
    case _:
      return 1 << L-1

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

def add(t, k, l, m, v):
  switch l:
    case 0:
      return t + v
    case _:
      (a, b) = t
      if k & m:
        return (a, add(b, k, l-1, m >> 1, v))
      else:
        return (add(a, k, l-1, m >> 1, v), b)

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

def walk(es, R, Q, S, l, m, lw, L, M):
  match es:
    case List/Nil:
      return (R, Q, S)
    case List/Cons:
      (u, v) = es.head
      R2 = setb(setb(R, (u << lw) | (v >> 4), L, M, 1 << (v & 15)), (v << lw) | (u >> 4), L, M, 1 << (u & 15))
      Q2 = push(push(Q, u, l, m, lambda $ru: 0), v, l, m, lambda $rv: 0)
      S2 = add(S, u, l, m, pa($ru, $rv, lw))
      return walk(es.tail, R2, Q2, S2, l, m, lw, L, M)

def pa(a, b, lw):
  switch lw:
    case 0:
      return popc(a & b)
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return pa(a1, b1, lw-1) + pa(a2, b2, lw-1)

def popc(x):
  a = x - ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b + (b >> 4)) & 3855
  return (c + (c >> 8)) & 31

def total(t, l):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      return total(a, l-1) + total(b, l-1)

# R has l + lw levels: the top l levels are the vertex, a leaf of Q meets a row subtree
def deliver_all(R, Q, l, lw):
  switch l:
    case 0:
      return deliver(R, Q)
    case _:
      (r1, r2) = R
      (q1, q2) = Q
      return deliver_all(r1, q1, l-1, lw) + deliver_all(r2, q2, l-1, lw)

def deliver(row, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(row) + deliver(row, sinks.tail)
