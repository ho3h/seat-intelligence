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
