# t3_wsp_dist: Bellman-Ford as a stream dataflow (see sps): every vertex runs its own process emitting its
# distance stream d_0 = (0 at s, INF elsewhere), d_{r+1} = min(d_r, d_r(w) + weight) over its neighbours'
# streams (read through wires set up during the edge walk), with a lagged global change stream for
# termination. Answer: the final distance at t.
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
# ---- sps (the ccs stream dataflow for Bellman-Ford distances: input i carries (w, stream)):
# (derived from) ccs: label propagation as a dataflow of streams (no rounds, no keyed routing after setup).
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
      (u, v, w) = es.head
      Sk2 = pushb(pushb(Sk, u, l, m, lambda $a: 0), v, l, m, lambda $b: 0)
      In2 = pushb(pushb(In, v, l, m, (w, $a)), u, l, m, (w, $b))
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
      (w, s) = t.e
      match s:
        case List/Nil:
          return (c, Br/Node((w, s), l2, r2))
        case List/Cons:
          y = s.head
          y2 = y + (y != 16777215) * w
          return (c - (c > y2) * (c - y2), Br/Node((w, s.tail), l2, r2))

def run(x, ins, G):
  match G:
    case List/Nil:
      return ([x], [], x)
    case List/Cons:
      if G.head:
        (y, ins2) = hmin(ins, x)
        (S, F, fin) = run(y, ins2, G.tail)
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
def procs(Sk, In, G, lv, v, src):
  switch lv:
    case 0:
      (S, F, fin) = run((v != src) * 16777215, In, G)
      return (fin, F, deliver(S, Sk))
    case _:
      (s1, s2) = Sk
      (i1, i2) = In
      h = 1 << (lv-1)
      (d1, f1, z1) = procs(s1, i1, G, lv-1, v, src)
      (d2, f2, z2) = procs(s2, i2, G, lv-1, v + h, src)
      return ((d1, d2), zipor(f1, f2), z1 + z2)

# distances from src for all 2^l vertices; returns (distance trie, 0)
def sps(es, l, m, src):
  (Sk, In) = swalk(es, zb(l), zb(l), l, m)
  gs = lambda $g: 0
  (D, C, z) = procs(Sk, In, $g, l, 0, src)
  return (D, z + gs(List/Cons(1, List/Cons(1, List/Cons(1, List/Cons(1, C))))))

# an empty list that waits for z (keeps the sink wiring alive in list outputs)
def nilz(z):
  if z == 0:
    return []
  else:
    return []
def prog(x):
  (n, s, t, es) = x
  if (s >= n) | (t >= n):
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    (D, z) = sps(es, l, m, s)
    return z + get(D, t, l, m)
