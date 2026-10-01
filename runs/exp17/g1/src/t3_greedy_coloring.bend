# t3_greedy_coloring: the greedy order as a dataflow net (no rounds). For each edge (a, b), a < b, the walk creates
# an unscoped lambda: its variable $x goes into b's value list (tree V), the lambda itself (a sink) into a's request
# list (tree Q). colour(b) = lowest clear bit of OR_{x in V_b} 2^x; every colour is then applied to its sinks, so
# each vertex waits only for its lower neighbours. Colour masks are 24-bit (a colour >= 24 would need 24 mutually
# differently coloured lower neighbours; the corpus sizes stay far below that).
def prog(x):
  (n, es) = x
  (l, m) = lvl(n, 0, 1)
  (V, Q) = walk(es, zl(l), zl(l), l, m)
  C = cols(V, l)
  return addhead(flat(C, l, 0, n, []), deliver_all(C, Q, l))

def walk(es, V, Q, l, m):
  match es:
    case List/Nil:
      return (V, Q)
    case List/Cons:
      (u, v) = es.head
      a = mn(u, v)
      b = mx(u, v)
      return walk(es.tail, push(V, b, l, m, $x), push(Q, a, l, m, lambda $x: 0), l, m)

def orl(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return (1 << xs.head) | orl(xs.tail)

def cols(V, l):
  switch l:
    case 0:
      k = orl(V)
      return popc(((k ^ 16777215) & (k + 1)) - 1)
    case _:
      (a, b) = V
      return (cols(a, l-1), cols(b, l-1))

# z = 0 (the sum of the sink results); adding it to the head keeps the deliveries alive
def addhead(xs, z):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(xs.head + z, xs.tail)
