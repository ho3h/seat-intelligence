# t3_walk_count: meet in the middle. Walks of length k from s to t = sum over v of (walks s ~> v of length k1) *
# (walks v ~> t of length k2), k1 + k2 = k. One list walk wires two channel networks (lib/chan_gen): forward (v
# listens to u for an arc u -> v) and backward (u listens to v). Each runs a fixed number of synchronous rounds with
# no global test (c_{r+1}(v) = sum of the neighbours' c_r, a balanced add over the Braun tree of input streams):
# ceil(k/2) rounds from s forwards and floor(k/2) from t backwards, in parallel. Answer: a balanced dot product.
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
# ---- chan_gen: lib/chan with input slots (meta, stream), hooks for the combine (pre(meta, head)/comb/unit), the state (st -> emitted value via out),
# the update (upd returns (new state, changed)), and the result (fin). Fixed-round runs are supported (run_fixed).
# ---- (chan) components by label propagation over pre-wired channels (streams) with a lagged global decision.
# Walk the edge list once. For edge (u, v) two unscoped lambdas are made: a sink at u whose variable is placed in
# v's input slots, and vice versa. After the walk each vertex is a persistent process: it applies every sink once
# to its own label stream S_v = [l0, l1, ...] (the stream is built lazily, round by round), and computes
# l_{r+1} = min(l_r, heads of its input streams) (a balanced Braun tree of streams, so a round is O(log deg) deep).
# Every vertex also emits a change stream; the change streams are OR-zipped up the vertex tree into O, and the
# decision stream is dec = [1] * K ++ O (fed back through an unscoped lambda): a vertex computes round r only if
# dec_r is 1, so the global OR latency overlaps K rounds of useful work (extra rounds are idempotent).
type Br:
  Node { e, l, r }
  Leaf

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

# per-vertex leaf: (inputs Braun tree, sinks list)
def zio(l):
  switch l:
    case 0:
      return (Br/Leaf, Br/Leaf)
    case _:
      return (zio(l-1), zio(l-1))

def addio(t, k, l, m, i, o):
  switch l:
    case 0:
      (ins, outs) = t
      return (bins(ins, i), bins(outs, o))
    case _:
      (a, b) = t
      if k & m:
        return (a, addio(b, k, l-1, m >> 1, i, o))
      else:
        return (addio(a, k, l-1, m >> 1, i, o), b)

def chan_walk(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v) = es.head
      T1 = addio(T, u, l, m, (0, $b), lambda $a: 0)
      return chan_walk(es.tail, addio(T1, v, l, m, (0, $a), lambda $b: 0), l, m)

# directed: an arc u -> v gives u a sink and v an input
def add_in(t, k, l, m, i):
  switch l:
    case 0:
      (ins, outs) = t
      return (bins(ins, i), outs)
    case _:
      (a, b) = t
      if k & m:
        return (a, add_in(b, k, l-1, m >> 1, i))
      else:
        return (add_in(a, k, l-1, m >> 1, i), b)

def add_out(t, k, l, m, o):
  switch l:
    case 0:
      (ins, outs) = t
      return (ins, bins(outs, o))
    case _:
      (a, b) = t
      if k & m:
        return (a, add_out(b, k, l-1, m >> 1, o))
      else:
        return (add_out(a, k, l-1, m >> 1, o), b)

def chan_walk_dir(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v) = es.head
      return chan_walk_dir(es.tail, add_in(add_out(T, u, l, m, lambda $a: 0), v, l, m, (0, $a)), l, m)

# weighted arcs forwards: for u -> v (weight w), v gets input (w, stream of u), u gets the sink
def chan_walk_fw(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v, w) = es.head
      return chan_walk_fw(es.tail, add_in(add_out(T, u, l, m, lambda $a: 0), v, l, m, (w, $a)), l, m)

# weighted arcs, listening backwards: for u -> v (weight w), u gets input (w, stream of v), v gets the sink
def chan_walk_back(es, T, l, m):
  match es:
    case List/Nil:
      return T
    case List/Cons:
      (u, v, w) = es.head
      return chan_walk_back(es.tail, add_in(add_out(T, v, l, m, lambda $a: 0), u, l, m, (w, $a)), l, m)

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

def ones(k, tl):
  switch k:
    case 0:
      return tl
    case _:
      return List/Cons(1, ones(k-1, tl))

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

# one round over the input streams: (combination of heads, tails)
def step(t, mode):
  match t:
    case Br/Leaf:
      return (unit(mode), Br/Leaf)
    case Br/Node:
      (a, ta) = step(t.l, mode)
      (b, tb) = step(t.r, mode)
      (meta, s) = t.e
      match s:
        case List/Nil:
          return (unit(mode), Br/Node((meta, s), ta, tb))
        case List/Cons:
          return (comb(mode, a, comb(mode, pre(mode, meta, s.head), b)), Br/Node((meta, s.tail), ta, tb))

def proc(st, ins, dec, mode, base):
  (S, C, f) = cont(st, ins, dec, mode, base)
  return (List/Cons(out(mode, st), S), C, f)

def cont(st, ins, dec, mode, base):
  match dec:
    case List/Nil:
      (tl, f) = fin(mode, base, st, ins)
      return (tl, [], f)
    case List/Cons:
      if dec.head:
        (x, ins2) = step(ins, mode)
        (ns, ch) = upd(mode, st, x)
        (S, C, f) = proc(ns, ins2, dec.tail, mode, base)
        return (S, List/Cons(ch, C), f)
      else:
        (tl, f) = fin(mode, base, st, ins)
        return (tl, [], f)

def deliver(S, outs):
  match outs:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = outs.e
      return f(S) + deliver(S, outs.l) + deliver(S, outs.r)

def run(T, mode, dec, l, base, n):
  switch l:
    case 0:
      if base < n:
        (ins, outs) = T
        (S, C, f) = proc(lab0(mode, base), ins, dec, mode, base)
        return (f, C, deliver(S, outs))
      else:
        return (0, [], 0)
    case _:
      (a, b) = T
      h = 1 << (l-1)
      (fa, ca, za) = run(a, mode, dec, l-1, base, n)
      (fb, cb, zb) = run(b, mode, dec, l-1, base + h, n)
      return ((fa, fb), zipor(ca, cb), za + zb)

# until no change (K speculative rounds hide the global OR): returns (result tree, zero)
def chan_gen(T, mode, K, l, n):
  dec = ones(K, $o)
  (F, O, z) = run(T, mode, dec, l, 0, n)
  sink = lambda $o: 0
  return (F, z + sink(O))

# exactly k rounds, no global test: returns (result tree, zero)
def run_fixed(T, mode, k, l, n):
  (F, O, z) = run(T, mode, ones(k, [0]), l, 0, n)
  return (F, z)

# force the delivery zero z before returning r (the sinks' results must be consumed, not erased)
def seq(z, r):
  switch z:
    case 0:
      return r
    case _:
      return r

def prog(x):
  (n, s, t, k, es) = x
  if (s >= n) | (t >= n):
    return 0
  else:
    (l, m) = lvl(n, 0, 1)
    (TF, TB) = walk2(es, zio(l), zio(l), l, m)
    (F, z1) = run_fixed(TF, s, (k + 1) / 2, l, n)
    (B, z2) = run_fixed(TB, t, k / 2, l, n)
    return z1 + z2 + dot(F, B, l, 0, n)

def walk2(es, TF, TB, l, m):
  match es:
    case List/Nil:
      return (TF, TB)
    case List/Cons:
      (u, v) = es.head
      TF2 = add_in(add_out(TF, u, l, m, lambda $a: 0), v, l, m, (0, $a))
      TB2 = add_in(add_out(TB, v, l, m, lambda $b: 0), u, l, m, (0, $b))
      return walk2(es.tail, TF2, TB2, l, m)

def dot(F, B, l, base, n):
  switch l:
    case 0:
      return (base < n) * F * B
    case _:
      (f1, f2) = F
      (b1, b2) = B
      h = 1 << (l-1)
      return dot(f1, b1, l-1, base, n) + dot(f2, b2, l-1, base + h, n)

def lab0(mode, base):
  return base == mode

def out(mode, st):
  return st

def pre(mode, meta, h):
  return h

def unit(mode):
  return 0

def comb(mode, a, b):
  return a + b

def upd(mode, st, x):
  return (x, 0)

def fin(mode, base, st, ins):
  return ([], st)
