# t5_rewrite_edges: bitsets + return wires, no data-dependent keyed routing.
# c walks: C = the clustering as a tuple tree (ltree), and node u pushes a placeholder $t_u into bucket c[u] of K
# (keys are input data, so these pushes collapse early), with the sink for $t_u at leaf u of P.
# edge walk (parallel): bucket u of E gets a placeholder $y for c[v] and bucket v one for c[u]; their sinks go to Q.
# After delivering C into Q: T_u = OR over E_u of onehot(c[v]) (a word-tree bitset over cluster ids); after
# delivering T into P: R_x = OR over K_x of T_u, the set of clusters adjacent to cluster x. Output: tail-threaded
# in-order listing of (x, y) for y in R_x with y > x (self loops and duplicates vanish in the bitset).
def prog(x):
  (c, es) = x
  (C, L, M) = ltree(c)
  lw = L - mn(L, 4)
  kb = L - lw
  (K, P) = cw(c, 0, zl(L), zl(L), L, M)
  (E, Q) = ew(es, zl(L), zl(L), L, M)
  T = ohs(E, L, lw, kb)
  z = deliver_all(C, Q, L) + deliver_all(T, P, L)
  return addz(fk(K, L, 0, lw, kb, []), z)

# z = 0 once every sink has been applied: the output is released through a switch on it, which keeps the
# deliveries alive (their placeholders feed the output)
def addz(xs, z):
  if z == 0:
    return xs
  else:
    return xs

def cw(xs, i, K, P, L, M):
  match xs:
    case List/Nil:
      return (K, P)
    case List/Cons:
      return cw(xs.tail, i + 1, push(K, xs.head, L, M, $t), push(P, i, L, M, lambda $t: 0), L, M)

def ew(es, E, Q, L, M):
  match es:
    case List/Nil:
      return (E, Q)
    case List/Cons:
      (u, v) = es.head
      E2 = push(push(E, u, L, M, $cv), v, L, M, $cu)
      Q2 = push(push(Q, v, L, M, lambda $cv: 0), u, L, M, lambda $cu: 0)
      return ew(es.tail, E2, Q2, L, M)

# bucket of cluster ids -> bitset
def ohs(E, l, lw, kb):
  switch l:
    case 0:
      return ohl(E, lw, kb)
    case _:
      (a, b) = E
      return (ohs(a, l-1, lw, kb), ohs(b, l-1, lw, kb))

def ohl(xs, lw, kb):
  match xs:
    case List/Nil:
      return zt(lw)
    case List/Cons:
      return ort(oh(xs.head, lw, 1 << (lw + 3)), ohl(xs.tail, lw, kb), lw)

# one-hot word tree (lw word levels, 16-bit words); m = weight of the current top word bit of y
def oh(y, lw, m):
  switch lw:
    case 0:
      return 1 << (y & 15)
    case _:
      if y & m:
        return (zt(lw-1), oh(y, lw-1, m >> 1))
      else:
        return (oh(y, lw-1, m >> 1), zt(lw-1))

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))

def orall(xs, lw):
  match xs:
    case List/Nil:
      return zt(lw)
    case List/Cons:
      return ort(xs.head, orall(xs.tail, lw), lw)

def fk(K, l, x, lw, kb, acc):
  switch l:
    case 0:
      match K:
        case List/Nil:
          return acc
        case List/Cons:
          return em(orall(K, lw), lw, 0, x, acc)
    case _:
      (a, b) = K
      h = 1 << (l-1)
      return fk(a, l-1, x, lw, kb, fk(b, l-1, x + h, lw, kb, acc))

def em(R, lw, base, x, acc):
  switch lw:
    case 0:
      return emw(R, 4, base, x, acc)
    case _:
      (r1, r2) = R
      h = 16 << (lw-1)
      return em(r1, lw-1, base, x, em(r2, lw-1, base + h, x, acc))

def emw(w, k, base, x, acc):
  if w == 0:
    return acc
  else:
    switch k:
      case 0:
        if base > x:
          return List/Cons((x, base), acc)
        else:
          return acc
      case _:
        h = 1 << (k-1)
        return emw(w & ((1 << h) - 1), k-1, base, x, emw(w >> h, k-1, base + h, x, acc))
