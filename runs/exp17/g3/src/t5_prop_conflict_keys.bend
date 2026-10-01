# t5_prop_conflict_keys: c is walked once into a Braun tree (index access O(log n), n counted on the way);
# every attribute reads c[x] and applies an order-independent "merge value" update at key (c[x], key) of a
# tuple trie (leaf: (seen, first value, conflict)); keyed updates collapse level by level along the walk.
# The conflicting leaves, in key order, are the sorted output.
#include base
#include braun
def prog(x):
  (cs, attrs) = x
  (C, n) = tobraun(cs, Br/Leaf, 0)
  (l, m) = lvl(n << 2, 0, 1)
  B = walk(attrs, C, n - 1, zt(l, (0, 0, 0)), l, m)
  return flat(B, l, 0, [])

def mv(t, k, l, m, v):
  switch l:
    case 0:
      (h, v0, cf) = t
      return (1, v0 * h + v * (1 - h), cf | (h & (v != v0)))
    case _:
      (a, b) = t
      if k & m:
        return (a, mv(b, k, l-1, m >> 1, v))
      else:
        return (mv(a, k, l-1, m >> 1, v), b)

def walk(es, C, n1, B, l, m):
  match es:
    case List/Nil:
      return B
    case List/Cons:
      (u, k, v) = es.head
      cu = bget(C, n1 - u)
      return walk(es.tail, C, n1, mv(B, (cu << 2) | k, l, m, v), l, m)

def flat(t, l, base, acc):
  switch l:
    case 0:
      (h, v0, cf) = t
      if cf:
        return List/Cons((base >> 2, base & 3), acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
