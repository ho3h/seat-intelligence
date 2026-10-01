def prog(x):
  (n, s, k, edges) = x
  words = (n + 23) / 24
  empty_bits = make_bits(words)
  start_bits = set_bit(empty_bits, s / 24, 1 << (s % 24))
  start = List/Cons(s, List/Nil)
  return bfs(edges, start, start_bits, start_bits, k, 1)

def make_bits(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(0, make_bits(n - 1))

def get_word(bits, index):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return bits.head
      else:
        return get_word(bits.tail, index - 1)

def set_bit(bits, index, mask):
  match bits:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if index == 0:
        return List/Cons(bits.head | mask, bits.tail)
      else:
        return List/Cons(bits.head, set_bit(bits.tail, index - 1, mask))

def has_bit(bits, vertex):
  word = get_word(bits, vertex / 24)
  mask = 1 << (vertex % 24)
  if (word & mask) == 0:
    return 0
  else:
    return 1

def merge_bits(a, b):
  match a:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match b:
        case List/Nil:
          return List/Nil
        case List/Cons:
          return List/Cons(a.head | b.head, merge_bits(a.tail, b.tail))

def add_candidate(vertex, seen_bits, nxt, nxt_bits, count):
  if has_bit(seen_bits, vertex) == 1:
    return (nxt, nxt_bits, count)
  else:
    if has_bit(nxt_bits, vertex) == 1:
      return (nxt, nxt_bits, count)
    else:
      mask = 1 << (vertex % 24)
      updated_bits = set_bit(nxt_bits, vertex / 24, mask)
      return (List/Cons(vertex, nxt), updated_bits, count + 1)

def scan_edges(edges, frontier_bits, seen_bits, nxt, nxt_bits, count):
  match edges:
    case List/Nil:
      return (nxt, nxt_bits, count)
    case List/Cons:
      (u, v) = edges.head
      if has_bit(frontier_bits, u) == 1:
        (nxt1, bits1, count1) = add_candidate(v, seen_bits, nxt, nxt_bits, count)
      else:
        (nxt1, bits1, count1) = (nxt, nxt_bits, count)
      if has_bit(frontier_bits, v) == 1:
        (nxt2, bits2, count2) = add_candidate(u, seen_bits, nxt1, bits1, count1)
      else:
        (nxt2, bits2, count2) = (nxt1, bits1, count1)
      return scan_edges(edges.tail, frontier_bits, seen_bits, nxt2, bits2, count2)

def bfs(edges, frontier, frontier_bits, seen_bits, remaining, total):
  if remaining == 0:
    return total
  else:
    match frontier:
      case List/Nil:
        return total
      case List/Cons:
        (nxt, nxt_bits, added) = scan_edges(edges, frontier_bits, seen_bits, List/Nil, make_bits((get_word_count(seen_bits))), 0)
        if added == 0:
          return total
        else:
          updated_seen = merge_bits(seen_bits, nxt_bits)
          return bfs(edges, nxt, nxt_bits, updated_seen, remaining - 1, total + added)

def get_word_count(bits):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + get_word_count(bits.tail)
