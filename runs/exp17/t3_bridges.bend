# t3_bridges: exact bridge test by subtree XOR of incident-edge bitsets over a BFS forest.
# 1. Channel label propagation (lib/chan_id) with labels root * 1024 + dist (min over neighbours + 1): every
#    vertex learns its component's smallest id and its BFS distance to it.
# 2. After the last round every vertex v picks its parent: the largest-id neighbour w with label(w) + 1 ==
#    label(v) (the slot metadata gives w and the edge index i), and appends (parent, S_v) to its stream, where
#    S_v = XOR of bit(i) over its incident edges XOR the S of the neighbours that chose v as parent (gated on
#    their parent field only, so the dataflow runs leaves-up without cycles).
# 3. S_v is the set of edges with exactly one end in v's subtree; the tree edge to v's parent is a bridge iff
#    S_v == {that edge}. Bitsets are balanced trees of 24-bit words (lib/bits), depth from the edge count.
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
# ---- chan_id: as lib/chan, but every input slot is (meta, stream) with meta = (neighbour id, edge index).
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

def chan_walk(es, T, l, m, i):
  match es:
    case List/Nil:
      return (T, i)
    case List/Cons:
      (u, v) = es.head
      T1 = addio(T, u, l, m, ((v, i), $b), lambda $a: 0)
      return chan_walk(es.tail, addio(T1, v, l, m, ((u, i), $a), lambda $b: 0), l, m, i + 1)

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
      (w, s) = t.e
      match s:
        case List/Nil:
          return (16777215, Br/Node((w, s), ta, tb))
        case List/Cons:
          h = s.head
          c = a - (a > b) * (a - b)
          return (h - (h > c) * (h - c), Br/Node((w, s.tail), ta, tb))

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

# force the delivery zero z before returning r (the sinks' results must be consumed, not erased)
def seq(z, r):
  switch z:
    case 0:
      return r
    case _:
      return r

# ---- bits: exact bitsets as balanced tuple-trees of 24-bit words (depth wl covers 24 * 2^wl bits)
def bzero(wl):
  switch wl:
    case 0:
      return 0
    case _:
      return (bzero(wl-1), bzero(wl-1))

def bit(i, wl):
  switch wl:
    case 0:
      return 1 << i
    case _:
      h = 24 << (wl-1)
      if i < h:
        return (bit(i, wl-1), bzero(wl-1))
      else:
        return (bzero(wl-1), bit(i - h, wl-1))

def bxor(a, b, wl):
  switch wl:
    case 0:
      return a ^ b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (bxor(a1, b1, wl-1), bxor(a2, b2, wl-1))

def beq(a, b, wl):
  switch wl:
    case 0:
      return a == b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return beq(a1, b1, wl-1) & beq(a2, b2, wl-1)

def bor(a, b, wl):
  switch wl:
    case 0:
      return a | b
    case _:
      (a1, a2) = a
      (b1, b2) = b
      return (bor(a1, b1, wl-1), bor(a2, b2, wl-1))

def pop24(x):
  x1 = x - ((x >> 1) & 5592405)
  x2 = (x1 & 3355443) + ((x1 >> 2) & 3355443)
  x3 = (x2 + (x2 >> 4)) & 986895
  return (x3 * 65793) >> 16

def bpop(a, wl):
  switch wl:
    case 0:
      return pop24(a)
    case _:
      (a1, a2) = a
      return bpop(a1, wl-1) + bpop(a2, wl-1)
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (T, cnt) = chan_walk(es, zio(l), l, m, 0)
  (wl, q) = lvl(cnt / 24 + 1, 0, 1)
  (F, z) = chan_gen(T, wl, 3, l, n)
  return z + tsum(F, l, 0, n)

def tsum(t, l, base, n):
  switch l:
    case 0:
      return (base < n) * t
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return tsum(a, l-1, base, n) + tsum(b, l-1, base + h, n)

def lab0(mode, base):
  return base * 1024

def upd(mode, lab, x):
  y = x + (x < 16777215)
  return lab - (lab > y) * (lab - y)

def fin(mode, base, lab, ins):
  (p, X, G) = scan(ins, lab, base, mode)
  S = bxor(X, G, mode)
  br = (p != 0) & beq(S, bit(p % 4096, mode), mode)
  return ([(p, S)], br)

# over the slots: (best parent candidate, XOR of incident edge bits, XOR of children's subtree sets)
def scan(t, lab, v, wl):
  match t:
    case Br/Leaf:
      return (0, bzero(wl), bzero(wl))
    case Br/Node:
      ((w, i), s) = t.e
      (p1, x1, g1) = scan(t.l, lab, v, wl)
      (p2, x2, g2) = scan(t.r, lab, v, wl)
      (lw, pw, sw) = last2(s)
      c = (lw + 1 == lab) * ((w + 1) * 4096 + i)
      g = gate(pw / 4096 == v + 1, sw, wl)
      return (max(c, max(p1, p2)), bxor(bit(i, wl), bxor(x1, x2, wl), wl), bxor(g, bxor(g1, g2, wl), wl))

def gate(ok, s, wl):
  if ok:
    return s
  else:
    return bzero(wl)

# the rest of a neighbour's stream after the last round: [label, (parent, S)]
def last2(s):
  match s:
    case List/Nil:
      return (16777215, 0, 0)
    case List/Cons:
      lw = s.head
      match s.tail:
        case List/Nil:
          return (lw, 0, 0)
        case List/Cons:
          (pw, sw) = s.tail.head
          return (lw, pw, sw)
