# t3_max_degree_vertex: degree trie keyed by vertex id (keyed increments collapse level by level during the
# list walk), then a balanced argmax reduction (ties to the left = smaller id).
#include base
def prog(x):
  (n, es) = x
  if n == 0:
    return 16777215
  else:
    (l, m) = lvl(n, 0, 1)
    C = walk(es, zt(l, 0), l, m)
    (d, i) = best(C, l, 0)
    return i

def walk(es, C, l, m):
  match es:
    case List/Nil:
      return C
    case List/Cons:
      (u, v) = es.head
      return walk(es.tail, inc(inc(C, u, l, m), v, l, m), l, m)

def best(t, l, base):
  switch l:
    case 0:
      return (t, base)
    case _:
      (a, b) = t
      h = 1 << (l-1)
      (da, ia) = best(a, l-1, base)
      (db, ib) = best(b, l-1, base + h)
      g = db > da
      return (da + g * (db - da), ia + g * (ib - ia))
