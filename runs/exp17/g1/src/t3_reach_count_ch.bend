# t3_reach_count: number of finite distances from s.
# directed frontier BFS with pre-wired channels: per arc u -> v one channel of unscoped lambdas (sender in u's
# out-list, receiver in v's in-list; keyed pushes collapse). Every vertex sends d + 1 on its out-channels and takes
# the min over its in-channels; B = 2 local rounds per batch, then a balanced OR decides (one-batch lookahead).
def prog(x):
  (n, s, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zoi(l), l, m)
  return cntf(loop(st0(A, l, 0, s), 1, l, 2), l)

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(A, u, v, l, m), l, m)

def st0(A, lv, base, s):
  switch lv:
    case 0:
      if base == s:
        return (0, A)
      else:
        return (16777215, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, s), st0(b, lv-1, base + h, s))
# @lpcore {"send": "x + (x < 16777215)"}

def cntf(t, l):
  switch l:
    case 0:
      return t < 16777215
    case _:
      (a, b) = t
      return cntf(a, l-1) + cntf(b, l-1)
