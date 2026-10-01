# t5_cluster_implied_unproposed: closure pairs = sum over clusters of s(s-1)/2, from max labels by a stream
# dataflow (see ccs) and a block-threaded keyed histogram of labels. Distinct input pairs:
# a trie of 16-bit words keyed by (u, v >> 4), each pair ORs one bit in during the list walk (keyed updates
# collapse level by level), then a popcount reduction.
# ---- base: tuple tries keyed by vertex id (MSB first), l levels, m = top-bit mask
type Br:
  Node { e, l, r }
  Leaf

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l, z):
  switch l:
    case 0:
      return z
    case _:
      return (zt(l-1, z), zt(l-1, z))

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

def get(t, k, l, m):
  switch l:
    case 0:
      return t
    case _:
      (a, b) = t
      if k & m:
        return get(b, k, l-1, m >> 1)
      else:
        return get(a, k, l-1, m >> 1)

def updmin(t, k, l, m, x):
  switch l:
    case 0:
      return t - (t > x) * (t - x)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmin(b, k, l-1, m >> 1, x))
      else:
        return (updmin(a, k, l-1, m >> 1, x), b)

def updmax(t, k, l, m, x):
  switch l:
    case 0:
      return t + (x > t) * (x - t)
    case _:
      (a, b) = t
      if k & m:
        return (a, updmax(b, k, l-1, m >> 1, x))
      else:
        return (updmax(a, k, l-1, m >> 1, x), b)
# ---- ccs: label propagation as a dataflow of streams (no rounds, no keyed routing after setup).
# Setup (during the edge walk): for each edge and each direction a fresh wire: the reader keeps $a in its
# input list, the writer keeps the sink (lambda $a: 0) in its sink list (keyed pushes into tuple tries).
# Each vertex then runs its own process: it emits its label stream s_0 = own id, s_{r+1} = min/max of s_r and
# the neighbours' s_r (read from a Braun tree of input streams in lockstep, O(log deg) per step), and a change-flag stream. The flag streams
# are OR-zipped over the vertex trie into the global stream C; a vertex continues past step r iff
# G[r] = 1 where G = [1, 1, 1, 1] ++ C (a lag of 4 steps hides the OR-reduce latency). G itself reaches the
# vertices through one more wire. At the end every vertex wires its stream into its sinks.
def pushl(t, k, l, m, v):
  switch l:
    case 0:
      return List/Cons(v, t)
    case _:
      (a, b) = t
      if k & m:
        return (a, pushl(b, k, l-1, m >> 1, v))
      else:
        return (pushl(a, k, l-1, m >> 1, v), b)

def swalk(es, Sk, In, l, m):
  match es:
    case List/Nil:
      return (Sk, In)
    case List/Cons:
      (u, v) = es.head
      Sk2 = pushb(pushb(Sk, u, l, m, lambda $a: 0), v, l, m, lambda $b: 0)
      In2 = pushb(pushb(In, v, l, m, $a), u, l, m, $b)
      return swalk(es.tail, Sk2, In2, l, m)

# inputs are a Braun tree of streams: min/max of the heads in O(log deg) depth, tails in the same shape
def hmin(t, x):
  match t:
    case Br/Leaf:
      return (x, Br/Leaf)
    case Br/Node:
      (a, l2) = hmin(t.l, x)
      (b, r2) = hmin(t.r, x)
      c = a - (a > b) * (a - b)
      s = t.e
      match s:
        case List/Nil:
          return (c, Br/Node(s, l2, r2))
        case List/Cons:
          y = s.head
          return (c - (c > y) * (c - y), Br/Node(s.tail, l2, r2))

def hmax(t, x):
  match t:
    case Br/Leaf:
      return (x, Br/Leaf)
    case Br/Node:
      (a, l2) = hmax(t.l, x)
      (b, r2) = hmax(t.r, x)
      c = a + (b > a) * (b - a)
      s = t.e
      match s:
        case List/Nil:
          return (c, Br/Node(s, l2, r2))
        case List/Cons:
          y = s.head
          return (c + (y > c) * (y - c), Br/Node(s.tail, l2, r2))

# mx = 1: max labels, mx = 0: min labels. Returns (label stream, flag stream, final label)
def run(x, ins, G, mx):
  match G:
    case List/Nil:
      return ([x], [], x)
    case List/Cons:
      if G.head:
        if mx:
          (y, ins2) = hmax(ins, x)
          (S, F, fin) = run(y, ins2, G.tail, mx)
          return (List/Cons(x, S), List/Cons(y != x, F), fin)
        else:
          (y, ins2) = hmin(ins, x)
          (S, F, fin) = run(y, ins2, G.tail, mx)
          return (List/Cons(x, S), List/Cons(y != x, F), fin)
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

# per vertex: run, deliver; returns (trie of final labels, OR-zipped flag stream, sink sum)
def procs(Sk, In, G, lv, v, mx, src):
  switch lv:
    case 0:
      (S, F, fin) = run(v + (src != 16777215) * ((v == src) - v), In, G, mx)
      return (fin, F, deliver(S, Sk))
    case _:
      (s1, s2) = Sk
      (i1, i2) = In
      h = 1 << (lv-1)
      (d1, f1, z1) = procs(s1, i1, G, lv-1, v, mx, src)
      (d2, f2, z2) = procs(s2, i2, G, lv-1, v + h, mx, src)
      return ((d1, d2), zipor(f1, f2), z1 + z2)

# component labels (min or max member) of all 2^l vertices; returns (label trie, 0).
# src != INF: labels start as (v == src), so max labels mark the vertices reachable from src.
def ccs(es, l, m, mx, src):
  (Sk, In) = swalk(es, zb(l), zb(l), l, m)
  gs = lambda $g: 0
  (D, C, z) = procs(Sk, In, $g, l, 0, mx, src)
  return (D, z + gs(List/Cons(1, List/Cons(1, List/Cons(1, List/Cons(1, C))))))

# an empty list that waits for z (keeps the sink wiring alive in list outputs)
def nilz(z):
  if z == 0:
    return []
  else:
    return []
# ---- scatkv: trie whose leaves are (key, x) -> trie C with C[key] = sum of x (x = 0 means nothing).
# Blocks of 8 leaves thread their keyed adds through a private zero trie; blocks are added pointwise.
def addt(a, b, l):
  switch l:
    case 0:
      return a + b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (addt(a1, b1, l-1), addt(a2, b2, l-1))

def addk(t, k, l, m, x):
  switch l:
    case 0:
      return t + x
    case _:
      (a, b) = t
      if k & m:
        return (a, addk(b, k, l-1, m >> 1, x))
      else:
        return (addk(a, k, l-1, m >> 1, x), b)

def skvt(KV, lv, l, m, C):
  switch lv:
    case 0:
      (k, x) = KV
      return addk(C, k, l, m, x)
    case _:
      (a, b) = KV
      return skvt(b, lv-1, l, m, skvt(a, lv-1, l, m, C))

def scatkv(KV, lv, l, m):
  if lv <= 3:
    return skvt(KV, lv, l, m, zt(l, 0))
  else:
    (a, b) = KV
    return addt(scatkv(a, lv - 1, l, m), scatkv(b, lv - 1, l, m), l)
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (l2, m2) = lvl((n + 15) >> 4, 0, 1)
  W = walkw(es, zt(l + l2, 0), l, m, l2, m << l2)
  (D, z) = ccs(es, l, m, 1, 16777215)
  C = scatkv(kv(D, l, 0, n), l, l, m)
  return z + pairs(C, l) - pops(W, l + l2)

def kv(D, l, base, n):
  switch l:
    case 0:
      return (D, base < n)
    case _:
      (a, b) = D
      h = 1 << (l-1)
      return (kv(a, l-1, base, n), kv(b, l-1, base + h, n))

def orb(t, k, l, m, b):
  switch l:
    case 0:
      return t | b
    case _:
      (a, c) = t
      if k & m:
        return (a, orb(c, k, l-1, m >> 1, b))
      else:
        return (orb(a, k, l-1, m >> 1, b), c)

def walkw(es, W, l, m, l2, mw):
  match es:
    case List/Nil:
      return W
    case List/Cons:
      (u, v) = es.head
      W2 = orb(W, (u << l2) | (v >> 4), l + l2, mw, 1 << (v & 15))
      return walkw(es.tail, W2, l, m, l2, mw)

def pairs(t, l):
  switch l:
    case 0:
      return (t * (t - 1)) / 2
    case _:
      (a, b) = t
      return pairs(a, l-1) + pairs(b, l-1)

def pop16(x):
  a = (x & 21845) + ((x >> 1) & 21845)
  b = (a & 13107) + ((a >> 2) & 13107)
  c = (b & 3855) + ((b >> 4) & 3855)
  return (c & 255) + (c >> 8)

def pops(t, l):
  switch l:
    case 0:
      return pop16(t)
    case _:
      (a, b) = t
      return pops(a, l-1) + pops(b, l-1)
