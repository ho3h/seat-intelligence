def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 0
  else:
    words = zeros((n + 23) / 24)
    bits_a = bit_mark(words, s)
    bits_b = bit_mark(words, t)
    return bidir(
      [(s, 0)], [(t, 0)],
      [(s, 0)], [(t, 0)],
      bits_a, bits_b, edges
    )

def bidir(front_a, front_b, seen_a, seen_b, bits_a, bits_b, edges):
  size_a = list_len(front_a)
  size_b = list_len(front_b)
  if size_a == 0:
    return 16777215
  else:
    if size_b == 0:
      return 16777215
    else:
      if size_a <= size_b:
        (next_a, next_seen_a, next_bits_a, best) =
          expand(front_a, [], seen_a, bits_a, seen_b, bits_b, edges, 16777215)
        if best != 16777215:
          return best
        else:
          return bidir(next_a, front_b, next_seen_a, seen_b, next_bits_a, bits_b, edges)
      else:
        (next_b, next_seen_b, next_bits_b, best) =
          expand(front_b, [], seen_b, bits_b, seen_a, bits_a, edges, 16777215)
        if best != 16777215:
          return best
        else:
          return bidir(front_a, next_b, seen_a, next_seen_b, bits_a, next_bits_b, edges)

def expand(frontier, next_frontier, own_seen, own_bits, other_seen, other_bits, edges, best):
  match frontier:
    case List/Nil:
      return (next_frontier, own_seen, own_bits, best)
    case List/Cons:
      (src, depth) = frontier.head
      (next2, own2, bits2, best2) =
        scan_edges(edges, src, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best)
      return expand(frontier.tail, next2, own2, bits2, other_seen, other_bits, edges, best2)

def scan_edges(edges, src, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best):
  match edges:
    case List/Nil:
      return (next_frontier, own_seen, own_bits, best)
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        (next2, own2, bits2, best2) =
          consider(v, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best)
        return scan_edges(edges.tail, src, depth, next2, own2, bits2, other_seen, other_bits, best2)
      else:
        if v == src:
          (next2, own2, bits2, best2) =
            consider(u, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best)
          return scan_edges(edges.tail, src, depth, next2, own2, bits2, other_seen, other_bits, best2)
        else:
          return scan_edges(edges.tail, src, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best)

def consider(v, depth, next_frontier, own_seen, own_bits, other_seen, other_bits, best):
  if bit_has(other_bits, v) == 1:
    other_dist = get_dist(other_seen, v)
    candidate = depth + 1 + other_dist
    if best == 16777215:
      best2 = candidate
    else:
      if candidate < best:
        best2 = candidate
      else:
        best2 = best
    return (next_frontier, own_seen, own_bits, best2)
  else:
    if bit_has(own_bits, v) == 0:
      next2 = List/Cons((v, depth + 1), next_frontier)
      own2 = List/Cons((v, depth + 1), own_seen)
      bits2 = bit_mark(own_bits, v)
      return (next2, own2, bits2, best)
    else:
      return (next_frontier, own_seen, own_bits, best)

def bit_has(bits, v):
  word = get_word(bits, v / 24)
  mask = 1 << (v % 24)
  if (word & mask) == 0:
    return 0
  else:
    return 1

def bit_mark(bits, v):
  return set_word(bits, v / 24, 1 << (v % 24))

def get_word(words, idx):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return words.head
      else:
        return get_word(words.tail, idx - 1)

def set_word(words, idx, mask):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, set_word(words.tail, idx - 1, mask))

def zeros(k):
  switch k:
    case 0:
      return []
    case _:
      return List/Cons(0, zeros(k - 1))

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
