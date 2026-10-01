# t5_cluster_count_ge: MAX-label propagation, then cluster sizes: groups of 16 leaves thread one count tree
# through keyed increments at their labels, and count trees add leafwise above that; then a balanced count >= k.
# channel LP core (see t3_cc_label): per undirected edge two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list, keyed pushes that collapse); rounds need no keyed routing; each vertex runs B = 2 rounds
# as a local dataflow loop, then a balanced OR decides, with the next batch spawned before the decision.
def prog(x):
  (n, k, es) = x
  (l, m) = lvl(n, 0, 1)
  A = walk(es, zoi(l), l, m)
  D = loop(st0(A, l, 0, n), 1, l, 2)
  return cge(sizes(D, l, l, m, 0, n), l, mx(k, 1))

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

# subtrees of 2^G leaves thread one count tree through keyed increments; above that, count trees add leafwise
def sizes(D, lv, l, m, base, n):
  if lv <= 4:
    return chain(D, lv, l, m, base, n, zt(l))
  else:
    (a, b) = D
    h = 1 << (lv - 1)
    return addt(sizes(a, lv - 1, l, m, base, n), sizes(b, lv - 1, l, m, base + h, n), l)

def chain(D, lv, l, m, base, n, T):
  switch lv:
    case 0:
      d = D
      if base < n:
        return addk(T, d, l, m, 1)
      else:
        return T
    case _:
      (a, b) = D
      h = 1 << (lv-1)
      return chain(b, lv-1, l, m, base + h, n, chain(a, lv-1, l, m, base, n, T))

def addt(a, b, l):
  switch l:
    case 0:
      return a + b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (addt(a1, b1, l-1), addt(a2, b2, l-1))

def cge(t, l, k):
  switch l:
    case 0:
      return t >= k
    case _:
      (a, b) = t
      return cge(a, l-1, k) + cge(b, l-1, k)
