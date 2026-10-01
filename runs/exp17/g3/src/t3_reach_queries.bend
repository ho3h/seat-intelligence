# t3_reach_queries: reachability rows R_v (bitsets of 16-bit words) as a stream dataflow: R_v^0 = {v},
# R_v^{r+1} = R_v^r | OR of R_w^r over successors w. Every vertex runs its own process, reading its
# successors' row streams through wires set up during the edge walk (a Braun tree of inputs, so the OR is
# O(log deg) deep) and wiring its own stream into its predecessors' inputs; a lagged global change stream
# (OR-zipped over the vertex trie) stops all processes together. Queries read bits of the final rows.
#include base
def prog(x):
  (n, qs, es) = x
  (l, m) = lvl(n, 0, 1)
  lb = l - (l > 4) * (l - 4)
  lw = l - lb
  (Sk, In) = swalk(es, zb(l), zb(l), l, m)
  gs = lambda $g: 0
  (D, C, z) = procs(Sk, In, $g, l, 0, lw)
  G = List/Cons(1, List/Cons(1, List/Cons(1, List/Cons(1, C))))
  return answer(qs, D, l, m, lw, z + gs(G))

def swalk(es, Sk, In, l, m):
  match es:
    case List/Nil:
      return (Sk, In)
    case List/Cons:
      (u, v) = es.head
      return swalk(es.tail, pushb(Sk, v, l, m, lambda $a: 0), pushb(In, u, l, m, $a), l, m)

def idrow(lw, wi, t, b):
  switch lw:
    case 0:
      return (wi == t) * b
    case _:
      h = 1 << (lw-1)
      return (idrow(lw-1, wi, t, b), idrow(lw-1, wi + h, t, b))

def ort(a, b, lw):
  switch lw:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (ort(a1, b1, lw-1), ort(a2, b2, lw-1))

def neqr(a, b, lw):
  switch lw:
    case 0:
      return a != b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return neqr(a1, b1, lw-1) | neqr(a2, b2, lw-1)

# OR of the head rows of a Braun tree of row streams into x; tails in the same shape
def hor(t, x, lw):
  match t:
    case Br/Leaf:
      return (x, Br/Leaf)
    case Br/Node:
      (a, l2) = hor(t.l, x, lw)
      (b, r2) = hor(t.r, a, lw)
      s = t.e
      match s:
        case List/Nil:
          return (b, Br/Node(s, l2, r2))
        case List/Cons:
          return (ort(b, s.head, lw), Br/Node(s.tail, l2, r2))

def run(x, ins, G, lw):
  match G:
    case List/Nil:
      return ([x], [], x)
    case List/Cons:
      if G.head:
        (y, ins2) = hor(ins, x, lw)
        (S, F, fin) = run(y, ins2, G.tail, lw)
        return (List/Cons(x, S), List/Cons(neqr(y, x, lw), F), fin)
      else:
        return ([x], [], x)

def deliver(S, sinks):
  match sinks:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = sinks.e
      return f(S) + deliver(S, sinks.l) + deliver(S, sinks.r)

def zipor(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          return List/Cons(a.head | b.head, zipor(a.tail, b.tail))

def procs(Sk, In, G, lv, v, lw):
  switch lv:
    case 0:
      (S, F, fin) = run(idrow(lw, 0, v >> 4, 1 << (v & 15)), In, G, lw)
      return (fin, F, deliver(S, Sk))
    case _:
      (s1, s2) = Sk
      (i1, i2) = In
      h = 1 << (lv-1)
      (d1, f1, z1) = procs(s1, i1, G, lv-1, v, lw)
      (d2, f2, z2) = procs(s2, i2, G, lv-1, v + h, lw)
      return ((d1, d2), zipor(f1, f2), z1 + z2)

def answer(qs, D, l, m, lw, z):
  match qs:
    case List/Nil:
      if z == 0:
        return []
      else:
        return []
    case List/Cons:
      (a, b) = qs.head
      w = get(get(D, a, l, m), b >> 4, lw, (1 << lw) >> 1)
      return List/Cons((w >> (b & 15)) & 1, answer(qs.tail, D, l, m, lw, z))
