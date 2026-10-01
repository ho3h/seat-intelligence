# Reconciliation core in Bend, weight-balanced channel ropes (variant of recon.bend.tmpl) (swing 27, G4 fairness). Same input as the native net of genome/exp16:
#   x = (n, L, tau, E, HE, M, HM)
#   E  perfect tuple tree of height HE; internal node (l, r), leaf (u, v, s); an edge is accepted iff s >= tau
#   M  perfect tuple tree of height HM; leaf (a, b, live) = must-not-link pair (live = 0 is padding)
# Output (canon, conflicts):
#   canon      list, entry i = largest ix in i's connected component under the accepted edges
#   conflicts  list of (a, b, c) for every live must-not-link pair with both ends in component c, in M order
#
# Algorithm (label propagation over per-edge channels, one-time scatter, lagged global stop decision):
#  1. Every accepted edge leaf makes two wires with Bend's unscoped lambdas: `lambda $a: 0` is a sink that u will feed
#     with its label stream, and `$a` is that stream as seen by v (and symmetrically $b). The two (input, sink) pairs
#     are placed at u and v in SPARSE vertex tries (a single path each); tries are merged pairwise up the edge tree.
#     Every live must-not-link leaf puts a probe sink at a and at b the same way.
#  2. Each vertex of the merged trie is a process: its label stream is [i, l1, l2, ...], l_{r+1} = max(l_r, heads of
#     its input streams); the stream is fed once to all its sinks (Bend auto-duplicates it). Each round also emits a
#     change flag; flags are OR-ed elementwise up the trie into one global flag stream G. Round r runs iff D[r] = 1,
#     D = [1]*K ++ G (K speculative rounds hide the reduce/broadcast latency; extra rounds after convergence are
#     idempotent). D is itself tied back into the trie with one more unscoped lambda.
#  3. The final label goes into the probe sinks; each must-not-link leaf compares its two probes.
#  4. canon is emitted from the trie of final labels with the tail threaded (all cells in parallel).

type S:
  Node { l, r }
  Leaf { ix, ch, h, pr }   # h = number of channels
  Emp

# channel rope; CT carries the sizes of its two children (weight-balanced joins)
type C:
  CT { hl, hr, a, b }
  CO { x }
  CZ

type R:
  Two { a, b }
  One { x }
  Z

type O:
  ONode { l, r }
  OLf { x }
  OEmp

def mx(a, b):
  if b > a:
    return b
  else:
    return a

# ---------------------------------------------------------------- sparse single path to key k (height h)
def path(k, h, p):
  switch h:
    case 0:
      return p
    case _:
      sub = path(k, h-1, p)
      switch (k >> h-1) & 1:
        case 0:
          return S/Node(sub, S/Emp)
        case _:
          return S/Node(S/Emp, sub)

# ---------------------------------------------------------------- merges (differ only at the leaf)
def mgE(a, b):
  match a:
    case S/Emp:
      return b
    case S/Node:
      match b:
        case S/Node:
          return S/Node(mgE(a.l, b.l), mgE(a.r, b.r))
        case S/Emp:
          return S/Node(a.l, a.r)
        case S/Leaf:
          return S/Emp
    case S/Leaf:
      match b:
        case S/Leaf:
          return S/Leaf(a.ix, cj(a.ch, a.h, b.ch, b.h), a.h + b.h, R/Z)
        case S/Emp:
          return S/Leaf(a.ix, a.ch, a.h, a.pr)
        case S/Node:
          return S/Emp

def mgM(a, b):
  match a:
    case S/Emp:
      return b
    case S/Node:
      match b:
        case S/Node:
          return S/Node(mgM(a.l, b.l), mgM(a.r, b.r))
        case S/Emp:
          return S/Node(a.l, a.r)
        case S/Leaf:
          return S/Emp
    case S/Leaf:
      match b:
        case S/Leaf:
          return S/Leaf(a.ix, C/CZ, 0, R/Two(a.pr, b.pr))
        case S/Emp:
          return S/Leaf(a.ix, a.ch, a.h, a.pr)
        case S/Node:
          return S/Emp

def mgF(a, b):
  match a:
    case S/Emp:
      return b
    case S/Node:
      match b:
        case S/Node:
          return S/Node(mgF(a.l, b.l), mgF(a.r, b.r))
        case S/Emp:
          return S/Node(a.l, a.r)
        case S/Leaf:
          return S/Emp
    case S/Leaf:
      match b:
        case S/Leaf:
          return S/Leaf(a.ix, a.ch, a.h, b.pr)
        case S/Emp:
          return S/Leaf(a.ix, a.ch, a.h, a.pr)
        case S/Node:
          return S/Emp

# ---------------------------------------------------------------- edge tree -> sparse trie of channel ends
def ew(E, h, L, tau):
  switch h:
    case 0:
      (u, v, s) = E
      if s < tau:
        return S/Emp
      else:
        pu = path(u, L, S/Leaf(u, C/CO(($b, lambda $a: 0)), 1, R/Z))
        pv = path(v, L, S/Leaf(v, C/CO(($a, lambda $b: 0)), 1, R/Z))
        return mgE(pu, pv)
    case _:
      (el, er) = E
      return mgE(ew(el, h-1, L, tau), ew(er, h-1, L, tau))

# ---------------------------------------------------------------- must-not-link tree -> probe trie + conflicts
def conf(a, b, x, y, tail):
  if x == y:
    return List/Cons((a, b, x), tail)
  else:
    return tail

def mw(M, h, L, tail):
  switch h:
    case 0:
      (a, b, live) = M
      switch live:
        case 0:
          return (S/Emp, tail)
        case _:
          ta = path(a, L, S/Leaf(a, C/CZ, 0, R/One(lambda $pa: 0)))
          tb = path(b, L, S/Leaf(b, C/CZ, 0, R/One(lambda $pb: 0)))
          return (mgM(ta, tb), conf(a, b, $pa, $pb, tail))
    case _:
      (ml, mr) = M
      (tr, cr) = mw(mr, h-1, L, tail)
      (tl, cl) = mw(ml, h-1, L, cr)
      return (mgM(tl, tr), cl)

# ---------------------------------------------------------------- vertex processes
def split(r):
  match r:
    case C/CT:
      (ia, sa) = split(r.a)
      (ib, sb) = split(r.b)
      return (R/Two(ia, ib), R/Two(sa, sb))
    case C/CO:
      (i, s) = r.x
      return (R/One(i), R/One(s))
    case C/CZ:
      return (R/Z, R/Z)

# weight-balanced join of two nonempty channel ropes of sizes na, nb (order is irrelevant: max and duplication are
# commutative). Sizes are plain sums, so the new top node is known after one match; the descent pipelines.
def cj(A, na, B, nb):
  if nb > na:
    return cj2(B, nb, A, na)
  else:
    return cj2(A, na, B, nb)

def cj2(A, na, B, nb):
  if na <= 2 * nb:
    return C/CT(na, nb, A, B)
  else:
    return cjd(A, B, nb)

def cjd(A, B, nb):
  match A:
    case C/CT:
      if A.hl <= A.hr:
        return C/CT(A.hl + nb, A.hr, cj(A.a, A.hl, B, nb), A.b)
      else:
        return C/CT(A.hl, A.hr + nb, A.a, cj(A.b, A.hr, B, nb))
    case _:
      return C/CZ

def feed(r, v):
  match r:
    case R/Two:
      return feed(r.a, v) + feed(r.b, v)
    case R/One:
      f = r.x
      return f(v)
    case R/Z:
      return 0

def pull(r):
  match r:
    case R/Two:
      (ma, ra) = pull(r.a)
      (mb, rb) = pull(r.b)
      return (mx(ma, mb), R/Two(ra, rb))
    case R/One:
      s = r.x
      match s:
        case List/Cons:
          return (s.head, R/One(s.tail))
        case List/Nil:
          return (0, R/Z)
    case R/Z:
      return (0, R/Z)

def go(lab, ins, D):
  match D:
    case List/Nil:
      return ([], [], lab)
    case List/Cons:
      switch D.head:
        case 0:
          return ([], [], lab)
        case _:
          (m, ins2) = pull(ins)
          new = mx(lab, m)
          (o, f, fin) = go(new, ins2, D.tail)
          return (List/Cons(lab, o), List/Cons(new != lab, f), fin)

def vtx(ix, ch, pr, D):
  match ch:
    case C/CZ:
      return ([], O/OLf(ix + feed(pr, ix)))
    case _:
      (ins, sinks) = split(ch)
      (out, fl, fin) = go(ix, ins, D)
      z1 = feed(sinks, out)
      return (fl, O/OLf(fin + z1 + feed(pr, fin)))

def orz(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return List/Cons(a.head, a.tail)
        case List/Cons:
          return List/Cons(a.head | b.head, orz(a.tail, b.tail))

def run(t, D):
  match t:
    case S/Emp:
      return ([], O/OEmp)
    case S/Node:
      (fl, ol) = run(t.l, D)
      (fr, orr) = run(t.r, D)
      return (orz(fl, fr), O/ONode(ol, orr))
    case S/Leaf:
      return vtx(t.ix, t.ch, t.pr, D)

# ---------------------------------------------------------------- output
def ids(base, h, n, tail):
  if base < n:
    switch h:
      case 0:
        return List/Cons(base, tail)
      case _:
        return ids(base, h-1, n, ids(base + (1 << h-1), h-1, n, tail))
  else:
    return tail

def tl(t, h, base, n, tail):
  match t:
    case O/OEmp:
      return ids(base, h, n, tail)
    case O/OLf:
      return List/Cons(t.x, tail)
    case O/ONode:
      h1 = h - 1
      return tl(t.l, h1, base, n, tl(t.r, h1, base + (1 << h1), n, tail))

def prog(x):
  (n, L, tau, E, HE, M, HM) = x
  te = ew(E, HE, L, tau)
  (tm, cf) = mw(M, HM, L, [])
  (F, fins) = run(mgF(te, tm), $d)
  z = (lambda $d: 0)(List/Cons(1, List/Cons(1, List/Cons(1, F))))
  return (tl(fins, L, z, n, []), cf)

def main():
  return prog(0)
