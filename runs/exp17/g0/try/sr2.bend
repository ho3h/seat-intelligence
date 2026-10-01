# t5_rewrite_sameas_roots: the pointer chase as a dataflow net (no rounds). Walking p, node i puts its output
# value (i if p[i] == i, else $r = whatever arrives in its sink) at index i of a Braun-indexed trie V, and pushes
# a "return address" sink (unscoped lambda) into a Braun tree at index p[i] of a trie Q. Braun indexing needs no
# size, so no length walk is needed and every insert is issued (and chained at the top, a few rounds each)
# while the walk is still reading the list. Then every node's own value is wired into the sinks at its index;
# roots ripple down the pointer forest as soon as they exist (acyclic by precondition, so nothing waits on itself).
type Br:
  Node { e, l, r }
  Leaf

type Tr:
  TN { v, l, r }
  TE

def prog(p):
  (out, Q, V) = walk(p, 0, Tr/TE, Tr/TE)
  return seq(dz(V, Q), out)

def seq(z, v):
  switch z:
    case 0:
      return v
    case _:
      return v

def bins(t, e):
  match t:
    case Br/Leaf:
      return Br/Node(e, Br/Leaf, Br/Leaf)
    case Br/Node:
      return Br/Node(e, bins(t.r, t.e), t.l)

# Braun indexing: 0 = this node, odd k -> left (k-1)/2, even k -> right (k-2)/2
def tset(t, k, v):
  match t:
    case Tr/TE:
      return tset(Tr/TN(0, Tr/TE, Tr/TE), k, v)
    case Tr/TN:
      if k == 0:
        return Tr/TN(v, t.l, t.r)
      else:
        if k & 1:
          return Tr/TN(t.v, tset(t.l, (k - 1) / 2, v), t.r)
        else:
          return Tr/TN(t.v, t.l, tset(t.r, (k - 2) / 2, v))

def tpush(t, k, f):
  match t:
    case Tr/TE:
      return tpush(Tr/TN(Br/Leaf, Tr/TE, Tr/TE), k, f)
    case Tr/TN:
      if k == 0:
        return Tr/TN(bins(t.v, f), t.l, t.r)
      else:
        if k & 1:
          return Tr/TN(t.v, tpush(t.l, (k - 1) / 2, f), t.r)
        else:
          return Tr/TN(t.v, t.l, tpush(t.r, (k - 2) / 2, f))

def pick(c, a, b):
  switch c:
    case 0:
      return b
    case _:
      return a

def walk(xs, i, Q, V):
  match xs:
    case List/Nil:
      return ([], Q, V)
    case List/Cons:
      t = xs.head
      v = pick(t == i, i, $r)
      (rest, Q2, V2) = walk(xs.tail, i + 1, tpush(Q, t, lambda $r: 0), tset(V, i, v))
      return (List/Cons(v, rest), Q2, V2)

def dz(V, Q):
  match Q:
    case Tr/TE:
      return 0
    case Tr/TN:
      match V:
        case Tr/TE:
          return 0
        case Tr/TN:
          return dl(V.v, Q.v) + dz(V.l, Q.l) + dz(V.r, Q.r)

def dl(v, t):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      f = t.e
      return f(v) + dl(v, t.l) + dl(v, t.r)
