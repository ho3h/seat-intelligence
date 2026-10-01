"""Generate the channel label-propagation core (Bend text) with per-program parameters."""
def core(op="mn", neut="16777215", better="x2 < x", send="x", B=2):
    return f'''
# ---- channel LP core: per vertex (label, (outs, ins)); outs = senders, ins = receivers ----
def lpq(A, l, m, s0):
  return loop(s0, 1, l, {B})

def loop(S, any, l, B):
  (S2, Lin, any2) = rall(S, l, B)
  if any:
    return loop(S2, any2, l, B)
  else:
    return Lin

def rall(S, lv, B):
  switch lv:
    case 0:
      (x, oi) = S
      (os, ins) = oi
      (x2, os2, ins2, ch) = vrun(x, os, ins, B, 0)
      return ((x2, (os2, ins2)), x, ch)
    case _:
      (a, b) = S
      (a2, la, fa) = rall(a, lv-1, B)
      (b2, lb, fb) = rall(b, lv-1, B)
      return ((a2, b2), (la, lb), fa | fb)

def vrun(x, os, ins, B, ch):
  switch B:
    case 0:
      return (x, os, ins, ch)
    case _:
      (os2, z) = csend(os, {send})
      (ins2, my) = crecv(ins)
      x2 = {op}(x, my)
      return vrun(x2, os2, ins2, B-1, ({better}) | z)

def csend(cs, x):
  match cs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      s = cs.head
      z = s((x, $n))
      (rest, zs) = csend(cs.tail, x)
      return (List/Cons(lambda $n: 0, rest), z | zs)

def crecv(cs):
  match cs:
    case List/Nil:
      return ([], {neut})
    case List/Cons:
      (y, r2) = cs.head
      (rest, my) = crecv(cs.tail)
      return (List/Cons(r2, rest), {op}(y, my))

# push a sender to u's outs and the matching receiver to v's ins (both keyed pushes; keys are input data)
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

# channel u -> v
def chan(A, u, v, l, m):
  return psi(pso(A, u, l, m, lambda $c: 0), v, l, m, $c)
# ---- end channel LP core ----
'''
