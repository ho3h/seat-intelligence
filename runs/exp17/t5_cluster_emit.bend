# t5_cluster_emit: components by channel label propagation (lib/chan) with labels 4095 - id (min over them is the
# largest member id), then one tail-threaded flatten emitting (d, canon) for every non-canonical d, ascending.
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
# ---- chan: components by label propagation over pre-wired channels (streams) with a lagged global decision.
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
      T1 = addio(T, u, l, m, $b, lambda $a: 0)
      return chan_walk(es.tail, addio(T1, v, l, m, $a, lambda $b: 0), l, m)

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
      return chan_walk_dir(es.tail, add_in(add_out(T, u, l, m, lambda $a: 0), v, l, m, $a), l, m)

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

# one round over the input streams: (min of heads, tails)
def step(t):
  match t:
    case Br/Leaf:
      return (16777215, Br/Leaf)
    case Br/Node:
      (a, ta) = step(t.l)
      (b, tb) = step(t.r)
      s = t.e
      match s:
        case List/Nil:
          return (16777215, Br/Node(s, ta, tb))
        case List/Cons:
          h = s.head
          c = h - (h > b) * (h - b)
          return (a - (a > c) * (a - c), Br/Node(s.tail, ta, tb))

# process: returns (label stream, change stream, result). upd(mode, lab, x) is the new label from the old one and the
# min of the neighbours' labels; fin(mode, base, lab, ins) = (stream tail appended after the last label, result).
# (A mode number selects the hooks: a global function passed as a value cannot be cloned by HVM2.)
def proc(lab, ins, dec, mode, base):
  (S, C, f) = cont(lab, ins, dec, mode, base)
  return (List/Cons(lab, S), C, f)

def cont(lab, ins, dec, mode, base):
  match dec:
    case List/Nil:
      (tl, f) = fin(mode, base, lab, ins)
      return (tl, [], f)
    case List/Cons:
      if dec.head:
        (x, ins2) = step(ins)
        nl = upd(mode, lab, x)
        (S, C, f) = proc(nl, ins2, dec.tail, mode, base)
        return (S, List/Cons(nl != lab, C), f)
      else:
        (tl, f) = fin(mode, base, lab, ins)
        return (tl, [], f)

def deliver(S, outs):
  match outs:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = outs.e
      return f(S) + deliver(S, outs.l) + deliver(S, outs.r)

# run all processes: returns (result tree, OR-zipped change stream, zero)
def run(T, mode, dec, l, base, n):
  switch l:
    case 0:
      if base < n:
        (ins, outs) = T
        (S, C, f) = proc(lab0(mode, base), ins, dec, mode, base)
        return (f, C, deliver(S, outs))
      else:
        return (16777215, [], 0)
    case _:
      (a, b) = T
      h = 1 << (l-1)
      (fa, ca, za) = run(a, mode, dec, l-1, base, n)
      (fb, cb, zb) = run(b, mode, dec, l-1, base + h, n)
      return ((fa, fb), zipor(ca, cb), za + zb)


# generic run over a built slot tree T: returns (result tree, zero)
def chan_gen(T, mode, K, l, n):
  dec = ones(K, $o)
  (F, O, z) = run(T, mode, dec, l, 0, n)
  sink = lambda $o: 0
  return (F, z + sink(O))

# components (mode 0: min label = smallest member; mode 1: labels 4095 - id, min = largest member)
def chan_run(T, mode, K, l, n):
  return chan_gen(T, mode, K, l, n)

# components: returns (label tree, zero, l, m) ; K = number of speculative rounds
def chan_cc(n, es, mode, K):
  (l, m) = lvl(n, 0, 1)
  T = chan_walk(es, zio(l), l, m)
  (F, z) = chan_run(T, mode, K, l, n)
  return (F, z, l, m)

# force the delivery zero z before returning r (the sinks' results must be consumed, not erased)
def seq(z, r):
  switch z:
    case 0:
      return r
    case _:
      return r

# ---- hooks for components: mode 0 labels = id (min = smallest member), mode 1 labels = 4095 - id (min = largest)
def lab0(mode, base):
  switch mode:
    case 0:
      return base
    case _:
      return 4095 - base

def upd(mode, lab, x):
  return lab - (lab > x) * (lab - x)

def fin(mode, base, lab, ins):
  return ([], lab)
def prog(x):
  (n, es) = x
  (F, z, l, m) = chan_cc(n, es, 1, 3)
  return seq(z, emit_pairs(F, l, 0, n, []))

def emit_pairs(t, l, base, n, acc):
  switch l:
    case 0:
      c = 4095 - t
      if (base < n) & (c != base):
        return List/Cons((base, c), acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return emit_pairs(a, l-1, base, n, emit_pairs(b, l-1, base + h, n, acc))
