# t3_forest_mis: rootless tree DP as an acyclic dataflow of edge messages (no rounds, no rooting).
# For every edge (u, v) the walk makes two one-shot wires (unscoped lambdas): m(u->v) and m(v->u). The message
# m(u->v) = (in, out) is the MIS DP of u's side of the forest with the edge cut, u included / excluded:
#   in = 1 + sum over u's other neighbours w of out(w->u),   out = sum over them of max(in, out)(w->u).
# Every vertex computes all its outgoing messages from the incoming ones with an exclusive-sum up/down pass over
# its Braun tree of slots, so m(u->v) never waits for m(v->u): in a forest the message graph is acyclic.
# Answer = sum over vertices of MIS(component, seen from the vertex) - sum over edges of MIS(component, seen from
# the edge), since every tree has one more vertex than edges. (in, out) are packed as in * 1024 + out (<= 128 each).
# ---- base: levels, constant trees, keyed increment, flatten (first n leaves, tail-threaded)
def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l):
  switch l:
    case 0:
      return 0
    case _:
      return (zt(l-1), zt(l-1))

def inc(t, k, l, m):
  switch l:
    case 0:
      return t + 1
    case _:
      (a, b) = t
      if k & m:
        return (a, inc(b, k, l-1, m >> 1))
      else:
        return (inc(a, k, l-1, m >> 1), b)

def flat(t, l, base, n, acc):
  switch l:
    case 0:
      if base < n:
        return List/Cons(t, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, n, flat(b, l-1, base + h, n, acc))

def max(a, b):
  return a + (b > a) * (b - a)

def min(a, b):
  return a - (a > b) * (a - b)
type Br:
  Node { e, l, r }
  Leaf

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  T = walk(es, zb(l), l, m)
  (vs, es2, z) = vert(T, l, 0, n)
  return z + vs - es2 / 2

def zb(l):
  switch l:
    case 0:
      return Br/Leaf
    case _:
      return (zb(l-1), zb(l-1))

def bins(t, e):
  match t:
    case Br/Leaf:
      return Br/Node(e, Br/Leaf, Br/Leaf)
    case Br/Node:
      return Br/Node(e, bins(t.r, t.e), t.l)

def pushb(t, k, l, m, e):
  switch l:
    case 0:
      return bins(t, e)
    case _:
      (a, b) = t
      if k & m:
        return (a, pushb(b, k, l-1, m >> 1, e))
      else:
        return (pushb(a, k, l-1, m >> 1, e), b)

def walk(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v) = es.head
      T1 = pushb(T, u, l, m, (lambda $a: 0, $b))
      return walk(es.tail, pushb(T1, v, l, m, (lambda $b: 0, $a)), l, m)

# up pass: subtree sums of the packed contributions (out, max(in, out)) of the incoming messages
def up(t):
  match t:
    case Br/Leaf:
      return (0, Br/Leaf)
    case Br/Node:
      (sink, x) = t.e
      xi = x / 1024
      xo = x % 1024
      c = xo * 1024 + max(xi, xo)
      (sl, tl) = up(t.l)
      (sr, tr) = up(t.r)
      return (sl + sr + c, Br/Node((sink, xi, xo, c, sl, sr), tl, tr))

# down pass: every slot gets the sum over all other slots, sends its message, and scores its edge
def down(t, o):
  match t:
    case Br/Leaf:
      return (0, 0)
    case Br/Node:
      (sink, xi, xo, c, sl, sr) = t.e
      ex = o + sl + sr
      mi = 1 + ex / 1024
      mo = ex % 1024
      z = sink(mi * 1024 + mo)
      e = max(mi + xo, mo + max(xi, xo))
      (z1, e1) = down(t.l, o + c + sr)
      (z2, e2) = down(t.r, o + c + sl)
      return (z + z1 + z2, e + e1 + e2)

# per vertex: (MIS of its component seen from it, sum of its slots' edge scores, zero)
def vert(T, l, base, n):
  switch l:
    case 0:
      if base < n:
        (s, t2) = up(T)
        (z, e) = down(t2, 0)
        return (max(1 + s / 1024, s % 1024), e, z)
      else:
        return (0, 0, 0)
    case _:
      (a, b) = T
      h = 1 << (l-1)
      (v1, e1, z1) = vert(a, l-1, base, n)
      (v2, e2, z2) = vert(b, l-1, base + h, n)
      return (v1 + v2, e1 + e2, z1 + z2)
