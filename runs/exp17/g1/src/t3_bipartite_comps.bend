# t3_bipartite_comps: min-label propagation on the doubled graph H (vertex (v, p) has key 2v+p; edge (u, v) links
# (u,0)-(v,1) and (u,1)-(v,0)). A component is bipartite iff for its smallest vertex r both 2r and 2r+1 keep
# their own labels; the answer counts such v.
# channel LP core (see t3_cc_label): per undirected edge two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list, keyed pushes that collapse); rounds need no keyed routing; each vertex runs B = 2 rounds
# as a local dataflow loop, then a balanced OR decides, with the next batch spawned before the decision.
def prog(x):
  (n, es) = x
  (l, m) = lvl(2 * n, 0, 1)
  A = walk(es, zoi(l), l, m)
  return bip(loop(st0(A, l, 0, 2 * n), 1, l, 2), l, 0, 2 * n)

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      u0 = 2 * u
      v0 = 2 * v
      A1 = chan(chan(A, u0, v0 + 1, l, m), v0 + 1, u0, l, m)
      return walk(es.tail, chan(chan(A1, u0 + 1, v0, l, m), v0, u0 + 1, l, m), l, m)

def st0(A, lv, base, n):
  switch lv:
    case 0:
      if base < n:
        return (base, A)
      else:
        return (16777215, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n), st0(b, lv-1, base + h, n))
# @lpcore {}

def bip(t, l, base, n2):
  switch l:
    case 0:
      return 0
    case _:
      (a, b) = t
      if l == 1:
        d0 = a
        d1 = b
        return (d0 == base) & (d1 == base + 1) & (base < n2)
      else:
        h = 1 << (l-1)
        return bip(a, l-1, base, n2) + bip(b, l-1, base + h, n2)
