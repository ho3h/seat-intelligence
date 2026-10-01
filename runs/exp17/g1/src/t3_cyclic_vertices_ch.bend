# t3_cyclic_vertices: reachability rows exchanged over pre-wired channels. Rows are word trees (16-bit words).
# For every arc v -> w the walk creates a channel of unscoped lambdas from w (sender) to v (receiver) (keyed pushes
# that collapse). A round: every vertex w sends R_w | {w}; every v ORs what it receives into R_v, so R_v converges
# to the set of vertices reachable from v by paths of length >= 1. No keyed routing, no matrix copies. Each vertex
# runs 2 local rounds per batch; a balanced OR of "the last round changed a row" decides, with the next batch
# spawned before the decision. v is cyclic iff v is in R_v.
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  lw = l - mn(l, 4)
  H = walk(es, zoi(l), l, m)
  S0 = st0(H, l, 0, n, lw)
  R = loop(S0, 1, l, lw)
  return diag(R, l, 0, lw)

def walk(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, chan(A, v, u, l, m), l, m)

def st0(A, lv, base, n, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (zt(lw), ork(zt(lw), base >> 4, lw, mw, (base < n) << (base & 15)), A)
    case _:
      (a, b) = A
      h = 1 << (lv-1)
      return (st0(a, lv-1, base, n, lw), st0(b, lv-1, base + h, n, lw))

def loop(S, any, l, lw):
  (S2, Rin, any2) = rall(S, l, lw)
  if any:
    return loop(S2, any2, l, lw)
  else:
    return Rin

# leaf: (R, own bit row, channels)
def rall(S, lv, lw):
  switch lv:
    case 0:
      (R, e, oi) = S
      (os, ins) = oi
      (R2, os2, ins2, ch) = vrun(R, e, os, ins, 2, 0, lw)
      return ((R2, e, (os2, ins2)), R, ch)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, lw)
      (b2, lb, fb) = rall(b, lv-1, lw)
      return ((a2, b2), (la, lb), fa | fb)

# ch = the last local round changed R
def vrun(R, e, os, ins, B, ch, lw):
  switch B:
    case 0:
      return (R, os, ins, ch)
    case _:
      (os2, z) = csend(os, ort(R, e, lw))
      (ins2, got) = crecv(ins, lw)
      R2 = ort(R, got, lw)
      return vrun(R2, e, os2, ins2, B-1, neq(R2, R, lw) | z, lw)

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

def diag(C, lv, base, lw):
  switch lv:
    case 0:
      (xx, mw) = lvl(1 << lw, 0, 1)
      return (getk(C, base >> 4, lw, mw) >> (base & 15)) & 1
    case _:
      (a, b) = C
      h = 1 << (lv-1)
      return diag(a, lv-1, base, lw) + diag(b, lv-1, base + h, lw)
