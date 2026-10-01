# t5_rewrite_neighbours: c is walked once into a Braun tree (index access in O(log n), n counted on the way);
# every edge reads c[u], c[v] and ORs a flag at key "the other end" into a vertex-keyed tuple trie when exactly
# one end maps to k (branch-free: a non-matching edge ORs 0). The trie's flagged leaves, in order.
#include base
#include braun
def prog(x):
  (k, cs, es) = x
  (C, n) = tobraun(cs, Br/Leaf, 0)
  (l, m) = lvl(n, 0, 1)
  F = walk(es, C, n - 1, k, zt(l, 0), l, m)
  return flat(F, l, 0, [])

def orb(t, k, l, m, b):
  switch l:
    case 0:
      return t | b
    case _:
      (a, c) = t
      if k & m:
        return (a, orb(c, k, l-1, m >> 1, b))
      else:
        return (orb(a, k, l-1, m >> 1, b), c)

def walk(es, C, n1, k, F, l, m):
  match es:
    case List/Nil:
      return F
    case List/Cons:
      (u, v) = es.head
      cu = bget(C, n1 - u)
      cv = bget(C, n1 - v)
      f = (cu == k) ^ (cv == k)
      return walk(es.tail, C, n1, k, orb(F, cu + cv - k, l, m, f), l, m)

def flat(t, l, base, acc):
  switch l:
    case 0:
      if t:
        return List/Cons(base, acc)
      else:
        return acc
    case _:
      (a, b) = t
      h = 1 << (l-1)
      return flat(a, l-1, base, flat(b, l-1, base + h, acc))
