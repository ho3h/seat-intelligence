# nolib (unchanged from runs/exp7/t3_dag_longest.bend)
# t3_dag_longest: the DP best[u] = max over edges u->v of 1 + best[v] as a dataflow net.
# Walk the edges once; for edge (u, v) create an unscoped lambda (a wire): its variable $x is pushed into the
# value list at leaf u of tree A, the lambda itself (a "sink") into the request list at leaf v of tree Q.
# best[] is computed leafwise from A; every best[v] is then wired into its sinks. Values ripple along the DAG
# with no rounds; the answer is a balanced max over best[].
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (A, Q) = walk(es, zl(l), zl(l), l, m)
  B = bests(A, l)
  return mxt(B, l) + deliver_all(B, Q, l)

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zl(l):
  switch l:
    case 0:
      return []
    case _:
      return (zl(l-1), zl(l-1))

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

def walk(es, A, Q, l, m):
  match es:
    case List/Nil:
      return (A, Q)
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, push(A, u, l, m, $x), push(Q, v, l, m, lambda $x: 0), l, m)

def max(a, b):
  return a + (b > a) * (b - a)

def best(vs):
  match vs:
    case List/Nil:
      return 0
    case List/Cons:
      return max(1 + vs.head, best(vs.tail))

def bests(A, l):
  switch l:
    case 0:
      return best(A)
    case _:
      (a, b) = A
      return (bests(a, l-1), bests(b, l-1))

def mxt(t, l):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      return max(mxt(a, l-1), mxt(b, l-1))

def deliver_all(B, Q, l):
  switch l:
    case 0:
      return deliver(B, Q)
    case _:
      (b1, b2) = B
      (q1, q2) = Q
      return deliver_all(b1, q1, l-1) + deliver_all(b2, q2, l-1)

def deliver(v, sinks):
  match sinks:
    case List/Nil:
      return 0
    case List/Cons:
      f = sinks.head
      return f(v) + deliver(v, sinks.tail)
