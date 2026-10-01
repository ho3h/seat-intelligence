# t5_cluster_canon: MAX-label propagation (labels start as own ids; padding leaves 0); output = labels.
# channel LP core (see t3_cc_label): per undirected edge two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list, keyed pushes that collapse); rounds need no keyed routing; each vertex runs B = 2 rounds
# as a local dataflow loop, then a balanced OR decides, with the next batch spawned before the decision.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zoi(l), l, m)
  return flat(loop(st0(A, l, 0, n), 1, l, 2), l, 0, n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(chan(A, u, v, l, m), v, u, l, m), l, m)

def st0(A, lv, base, n):
  switch lv:
    case 0:
      if base < n:
        return (base, A)
      else:
        return (0, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n), st0(b, lv-1, base + h, n))
# @lpcore {"op": "mx", "neut": "0", "better": "x2 > x"}
