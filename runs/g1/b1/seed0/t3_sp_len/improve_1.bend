def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 0
  else:
    return bidir([(s, 0)], [(t, 0)], [(s, 0)], [(t, 0)], edges)

def bidir(front_a, front_b, seen_a, seen_b, edges):
  size_a = list_len(front_a)
  size_b = list_len(front_b)
  if size_a == 0:
    return 16777215
  else:
    if size_b == 0:
      return 16777215
    else:
      if size_a <= size_b:
        (next_a, next_seen_a, best) = expand(front_a, [], seen_a, seen_b, edges, 16777215)
        if best != 16777215:
          return best
        else:
          return bidir(next_a, front_b, next_seen_a, seen_b, edges)
      else:
        (next_b, next_seen_b, best) = expand(front_b, [], seen_b, seen_a, edges, 16777215)
        if best != 16777215:
          return best
        else:
          return bidir(front_a, next_b, seen_a, next_seen_b, edges)

def expand(frontier, next_frontier, own_seen, other_seen, edges, best):
  match frontier:
    case List/Nil:
      return (next_frontier, own_seen, best)
    case List/Cons:
      (src, depth) = frontier.head
      (next2, own2, best2) = scan_edges(edges, src, depth, next_frontier, own_seen, other_seen, best)
      return expand(frontier.tail, next2, own2, other_seen, edges, best2)

def scan_edges(edges, src, depth, next_frontier, own_seen, other_seen, best):
  match edges:
    case List/Nil:
      return (next_frontier, own_seen, best)
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        (next2, own2, best2) = consider(v, depth, next_frontier, own_seen, other_seen, best)
        return scan_edges(edges.tail, src, depth, next2, own2, other_seen, best2)
      else:
        if v == src:
          (next2, own2, best2) = consider(u, depth, next_frontier, own_seen, other_seen, best)
          return scan_edges(edges.tail, src, depth, next2, own2, other_seen, best2)
        else:
          return scan_edges(edges.tail, src, depth, next_frontier, own_seen, other_seen, best)

def consider(v, depth, next_frontier, own_seen, other_seen, best):
  other_dist = get_dist(other_seen, v)
  if other_dist != 16777215:
    candidate = depth + 1 + other_dist
    if best == 16777215:
      best2 = candidate
    else:
      if candidate < best:
        best2 = candidate
      else:
        best2 = best
    return (next_frontier, own_seen, best2)
  else:
    own_dist = get_dist(own_seen, v)
    if own_dist == 16777215:
      next2 = List/Cons((v, depth + 1), next_frontier)
      own2 = List/Cons((v, depth + 1), own_seen)
      return (next2, own2, best)
    else:
      return (next_frontier, own_seen, best)

def get_dist(seen, v):
  match seen:
    case List/Nil:
      return 16777215
    case List/Cons:
      (node, dist) = seen.head
      if node == v:
        return dist
      else:
        return get_dist(seen.tail, v)

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)
