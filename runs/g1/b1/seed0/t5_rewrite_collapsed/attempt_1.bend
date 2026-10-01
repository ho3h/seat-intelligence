def prog(x):
  (clusters, edges) = x
  return process(edges, clusters, [], 0)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return at(xs.tail, i - 1)

def has_pair(pairs, x, y):
  match pairs:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = pairs.head
      if a == x:
        if b == y:
          return 1
        else:
          return has_pair(pairs.tail, x, y)
      else:
        return has_pair(pairs.tail, x, y)

def process(edges, clusters, seen, collapsed):
  match edges:
    case List/Nil:
      return collapsed
    case List/Cons:
      (u, v) = edges.head
      cu = at(clusters, u)
      cv = at(clusters, v)
      if cu == cv:
        return process(edges.tail, clusters, seen, collapsed + 1)
      else:
        if cu < cv:
          lo = cu
          hi = cv
        else:
          lo = cv
          hi = cu
        if has_pair(seen, lo, hi) == 1:
          return process(edges.tail, clusters, seen, collapsed + 1)
        else:
          return process(edges.tail, clusters, List/Cons((lo, hi), seen), collapsed)
