# ---- ccu (ungated emission: every vertex re-emits its label every round, so the update chain's
# control never waits for data): frontier label propagation (max or min label) over tuple tries.
# A: adjacency, leaf = Braun tree of neighbour ids. D: leaf = (label, improved flag).
# mx = 1: labels grow to the component max (neutral 0); mx = 0: labels shrink to the component min (neutral INF).
def walkp(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walkp(es.tail, pushb(pushb(A, u, l, m, v), v, l, m, u), l, m)

def ebx(t, d, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      return ebx(t.r, d, ebx(t.l, d, updmax(N, t.e, l, m, d), l, m), l, m)

def ebn(t, d, N, l, m):
  match t:
    case Br/Leaf:
      return N
    case Br/Node:
      return ebn(t.r, d, ebn(t.l, d, updmin(N, t.e, l, m, d), l, m), l, m)

def emitx(A, D, l, lv, m, N):
  switch lv:
    case 0:
      (d, f) = D
      return ebx(A, d, N, l, m)
    case _:
      (a1, a2) = A
      (d1, d2) = D
      return emitx(a2, d2, l, lv-1, m, emitx(a1, d1, l, lv-1, m, N))

def emitn(A, D, l, lv, m, N):
  switch lv:
    case 0:
      (d, f) = D
      return ebn(A, d, N, l, m)
    case _:
      (a1, a2) = A
      (d1, d2) = D
      return emitn(a2, d2, l, lv-1, m, emitn(a1, d1, l, lv-1, m, N))

def mergex(D, N, lv):
  switch lv:
    case 0:
      (d, f) = D
      t = N > d
      return ((d + t * (N - d), t), t)
    case _:
      (d1, d2) = D
      (n1, n2) = N
      (x1, a1) = mergex(d1, n1, lv-1)
      (x2, a2) = mergex(d2, n2, lv-1)
      return ((x1, x2), a1 | a2)

def mergen(D, N, lv):
  switch lv:
    case 0:
      (d, f) = D
      t = N < d
      return ((d - t * (d - N), t), t)
    case _:
      (d1, d2) = D
      (n1, n2) = N
      (x1, a1) = mergen(d1, n1, lv-1)
      (x2, a2) = mergen(d2, n2, lv-1)
      return ((x1, x2), a1 | a2)

def loopx(A, D, N, l, m):
  (D2, any) = mergex(D, N, l)
  N2 = emitx(A, D2, l, l, m, zt(l, 0))
  if any:
    return loopx(A, D2, N2, l, m)
  else:
    return D2

def loopn(A, D, N, l, m):
  (D2, any) = mergen(D, N, l)
  N2 = emitn(A, D2, l, l, m, zt(l, 16777215))
  if any:
    return loopn(A, D2, N2, l, m)
  else:
    return D2

# initial labels: own id, flagged; padding leaves get the neutral, unflagged
def initl(l, base, n, z):
  switch l:
    case 0:
      if base < n:
        return (base, 1)
      else:
        return (z, 0)
    case _:
      h = 1 << (l-1)
      return (initl(l-1, base, n, z), initl(l-1, base + h, n, z))

# labels of all vertices: component max (mx=1) or min (mx=0)
def ccmax(A, n, l, m):
  D0 = initl(l, 0, n, 0)
  return loopx(A, D0, emitx(A, D0, l, l, m, zt(l, 0)), l, m)

def ccmin(A, n, l, m):
  D0 = initl(l, 0, n, 16777215)
  return loopn(A, D0, emitn(A, D0, l, l, m, zt(l, 16777215)), l, m)

# single-source reach from s: leaf = (1 if reached, flag)
def inits(l, base, s):
  switch l:
    case 0:
      if base == s:
        return (1, 1)
      else:
        return (0, 0)
    case _:
      h = 1 << (l-1)
      return (inits(l-1, base, s), inits(l-1, base + h, s))

def reach(A, s, l, m):
  D0 = inits(l, 0, s)
  return loopx(A, D0, emitx(A, D0, l, l, m, zt(l, 0)), l, m)
