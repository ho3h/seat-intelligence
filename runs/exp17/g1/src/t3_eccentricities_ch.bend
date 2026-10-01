# t3_eccentricities: all-sources BFS as bitset rows exchanged over pre-wired channels. Rows are word trees
# (16-bit words). Per undirected edge the walk creates two channels of unscoped lambdas (sender in u's out-list,
# receiver in v's in-list; keyed pushes that collapse). A round: every vertex sends its ball R_v (and a fresh
# `lambda $next` becomes the channel's next sender) and ORs the rows it receives: R'_v = R_v | OR R_u. No keyed
# routing and no copying of the whole matrix per vertex. ecc(v) = number of rounds in which R_v was not yet full.
# Each vertex runs 2 local rounds per batch; a balanced OR of "some ball not full" decides, with the next batch
# spawned before the decision (one-batch lookahead).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  H = walk(es, zoi(l), l, m)
  F = full(lw, 0, n)
  S0 = st0(H, l, 0, n, lw)
  E = loop(S0, 1, l, F, lw)
  return flat(E, l, 0, n, [])

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(chan(A, u, v, l, m), v, u, l, m), l, m)

def st0(A, lv, base, n, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (ork(zt(lw), base >> 4, lw, mw, (base < n) << (base & 15)), 0, base < n, A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n, lw), st0(b, lv-1, base + h, n, lw))

def loop(S, any, l, F, lw):
  (S2, Ein, any2) = rall(S, l, F, lw)
  if any:
    return loop(S2, any2, l, F, lw)
  else:
    return Ein

def rall(S, lv, F, lw):
  switch lv:
    case 0:
      (R, E, real, oi) = S
      (os, ins) = oi
      (R2, E2, os2, ins2, nf) = vrun(R, E, real, os, ins, 2, F, lw)
      return ((R2, E2, real, (os2, ins2)), E, nf)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, F, lw)
      (b2, lb, fb) = rall(b, lv-1, F, lw)
      return ((a2, b2), (la, lb), fa | fb)

# nf of the returned state = its ball is still not full
def vrun(R, E, real, os, ins, B, F, lw):
  nf = real & neq(R, F, lw)
  switch B:
    case 0:
      return (R, E, os, ins, nf)
    case _:
      (os2, z) = csend(os, R)
      (ins2, got) = crecv(ins, lw)
      return vrun(ort(R, got, lw), E + nf + z, real, os2, ins2, B-1, F, lw)

def csend(cs, x):
  match cs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      s = cs.head
      z = s((x, $n))
      (rest, zs) = csend(cs.tail, x)
      return (List/Cons(lambda $n: 0, rest), z | zs)

def crecv(cs, lw):
  match cs:
    case List/Nil:
      return ([], zt(lw))
    case List/Cons:
      (y, r2) = cs.head
      (rest, my) = crecv(cs.tail, lw)
      return (List/Cons(r2, rest), ort(y, my, lw))

def pso(t, k, l, m, v):
  switch l:
    case 0:
      (os, ins) = t
      return (List/Cons(v, os), ins)
    case _:
      (a, b) = t
      if k & m:
        return (a, pso(b, k, l-1, m >> 1, v))
      else:
        return (pso(a, k, l-1, m >> 1, v), b)

def psi(t, k, l, m, v):
  switch l:
    case 0:
      (os, ins) = t
      return (os, List/Cons(v, ins))
    case _:
      (a, b) = t
      if k & m:
        return (a, psi(b, k, l-1, m >> 1, v))
      else:
        return (psi(a, k, l-1, m >> 1, v), b)

def zoi(l):
  switch l:
    case 0:
      return ([], [])
    case _:
      return (zoi(l-1), zoi(l-1))

def chan(A, u, v, l, m):
  return psi(pso(A, u, l, m, lambda $c: 0), v, l, m, $c)

def full(lw, base, n):
  switch lw:
    case 0:
      k = n - mn(n, base)
      return (1 << mn(k, 16)) - 1
    case _:
      h = 16 << (lw-1)
      return (full(lw-1, base, n), full(lw-1, base + h, n))

def neq(a, b, L):
  switch L:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neq(a1, b1, L-1) | neq(a2, b2, L-1)

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))
