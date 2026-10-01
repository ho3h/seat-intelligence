# t5_prop_conflicts: three walks in parallel, joined by return wires (unscoped lambdas).
# attrs walk: keyed sets into A (tree keyed by node*4 + key; leaf (min, max) = (v, v), empty (INF, 0)).
# c walk: node i pushes a placeholder $a_i into bucket c[i] of G (keys are input data, so the pushes collapse
# early) and the sink "lambda $a_i" into leaf i of S. Delivery wires node i's 4-slot subtree of A into its
# placeholder; each cluster folds its members' slots leafwise with (min, max) and counts slots with min < max.
def prog(x):
  (c, at) = x
  (L, M) = lvl(ln(c, 0), 0, 1)
  (G, S) = cw(c, 0, zl(L), zl(L), L, M)
  A = aw(at, emp(L + 2), L + 2, M << 2)
  return cnt(G, L) + deliver_all(A, S, L)

def emp(l):
  switch l:
    case 0:
      return (16777215, 0)
    case _:
      return (emp(l-1), emp(l-1))

def cw(xs, i, G, S, L, M):
  match xs:
    case List/Nil:
      return (G, S)
    case List/Cons:
      return cw(xs.tail, i + 1, push(G, xs.head, L, M, $a), push(S, i, L, M, lambda $a: 0), L, M)

def aw(xs, A, L2, M2):
  match xs:
    case List/Nil:
      return A
    case List/Cons:
      (nd, k, v) = xs.head
      return aw(xs.tail, setk(A, (nd << 2) | k, L2, M2, (v, v)), L2, M2)

def cnt(G, l):
  switch l:
    case 0:
      return confl(fold4(G))
    case _:
      (a, b) = G
      return cnt(a, l-1) + cnt(b, l-1)

def fold4(xs):
  match xs:
    case List/Nil:
      return emp(2)
    case List/Cons:
      return comb(xs.head, fold4(xs.tail), 2)

def comb(a, b, l):
  switch l:
    case 0:
      (a1, a2) = a
      (b1, b2) = b
      return (mn(a1, b1), mx(a2, b2))
    case _:
      (x1, x2) = a
      (y1, y2) = b
      return (comb(x1, y1, l-1), comb(x2, y2, l-1))

def confl(s):
  ((s0, s1), (s2, s3)) = s
  return lt(s0) + lt(s1) + lt(s2) + lt(s3)

def lt(p):
  (a, b) = p
  return a < b
