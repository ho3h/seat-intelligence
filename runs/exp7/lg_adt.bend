# control: line_graph_edges with an ADT tree (match on the node) instead of tuple destructuring
type T:
  Node { l, r }
  Leaf { v }

def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  return pairs(walk(es, zt(l), l, m))

def lvl(n, l, p):
  if p >= n:
    return (l, p >> 1)
  else:
    return lvl(n, l + 1, p << 1)

def zt(l):
  switch l:
    case 0:
      return T/Leaf(0)
    case _:
      return T/Node(zt(l-1), zt(l-1))

def inc(t, k, m):
  match t:
    case T/Leaf:
      return T/Leaf(t.v + 1)
    case T/Node:
      if k & m:
        return T/Node(t.l, inc(t.r, k, m >> 1))
      else:
        return T/Node(inc(t.l, k, m >> 1), t.r)

def walk(es, t, l, m):
  match es:
    case List/Nil:
      return t
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, inc(inc(t, u, m), v, m), l, m)

def pairs(t):
  match t:
    case T/Leaf:
      return (t.v * (t.v - 1)) / 2
    case T/Node:
      return pairs(t.l) + pairs(t.r)
