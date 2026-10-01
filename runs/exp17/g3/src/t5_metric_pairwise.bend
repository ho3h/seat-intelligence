# t5_metric_pairwise: both label lists are walked (in parallel) into Braun trees of the same shape and zipped;
# then every element counts, over the whole tree, the elements with equal pred, equal truth, and both
# (balanced reductions, all elements at once; for n < 256 the three counts are packed in one number). Ordered pairs including i == i: tp = (both - n)/2, etc.
#include base
#include braun
def prog(x):
  (ps, ts) = x
  (P, n) = tobraun(ps, Br/Leaf, 0)
  (T, n2) = tobraun(ts, Br/Leaf, 0)
  Z = zipb(P, T)
  if n < 256:
    (a, b, c) = outer8(Z, Z)
  else:
    (a, b, c) = outer(Z, Z)
  tp = (c - n) >> 1
  return (tp, ((a - n) >> 1) - tp, ((b - n) >> 1) - tp)

def zipb(p, t):
  match p:
    case Br/Leaf:
      return Br/Leaf
    case Br/Node:
      match t:
        case Br/Leaf:
          return Br/Leaf
        case Br/Node:
          return Br/Node((p.e, t.e), zipb(p.l, t.l), zipb(p.r, t.r))

def inner(t, p, q):
  match t:
    case Br/Leaf:
      return (0, 0, 0)
    case Br/Node:
      (p2, q2) = t.e
      (a1, b1, c1) = inner(t.l, p, q)
      (a2, b2, c2) = inner(t.r, p, q)
      e1 = p2 == p
      e2 = q2 == q
      return (a1 + a2 + e1, b1 + b2 + e2, c1 + c2 + (e1 & e2))

def outer(t, Z):
  match t:
    case Br/Leaf:
      return (0, 0, 0)
    case Br/Node:
      (p, q) = t.e
      (a0, b0, c0) = inner(Z, p, q)
      (a1, b1, c1) = outer(t.l, Z)
      (a2, b2, c2) = outer(t.r, Z)
      return (a0 + a1 + a2, b0 + b1 + b2, c0 + c1 + c2)

# n < 256: the three per-element counts fit in one packed number (8 bits each)
def inner8(t, p, q):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      (p2, q2) = t.e
      e1 = p2 == p
      e2 = q2 == q
      return inner8(t.l, p, q) + inner8(t.r, p, q) + e1 + (e2 << 8) + ((e1 & e2) << 16)

def outer8(t, Z):
  match t:
    case Br/Leaf:
      return (0, 0, 0)
    case Br/Node:
      (p, q) = t.e
      v = inner8(Z, p, q)
      (a1, b1, c1) = outer8(t.l, Z)
      (a2, b2, c2) = outer8(t.r, Z)
      return ((v & 255) + a1 + a2, ((v >> 8) & 255) + b1 + b2, (v >> 16) + c1 + c2)
