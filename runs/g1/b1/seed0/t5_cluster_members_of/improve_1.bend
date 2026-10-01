def prog(x):
  (n, target, pairs) = x
  chunks = (n + 23) / 24
  initial = set_bit(make_masks(chunks), target)
  reversed_pairs = reverse_pairs(pairs, [])
  reached = closure(pairs, reversed_pairs, initial)
  return members(n, reached, [])

def make_masks(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, make_masks(count - 1))

def reverse_pairs(pairs, acc):
  match pairs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_pairs(pairs.tail, List/Cons(pairs.head, acc))

def get_chunk(bits, index):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return bits.head
      else:
        return get_chunk(bits.tail, index - 1)

def set_chunk(bits, index, flag):
  match bits:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(bits.head | flag, bits.tail)
      else:
        return List/Cons(bits.head, set_chunk(bits.tail, index - 1, flag))

def has_bit(bits, node):
  index = node / 24
  offset = node % 24
  mask = 1 << offset
  return (get_chunk(bits, index) & mask) != 0

def set_bit(bits, node):
  index = node / 24
  offset = node % 24
  mask = 1 << offset
  return set_chunk(bits, index, mask)

def scan_edges(pairs, reached, changed):
  match pairs:
    case List/Nil:
      return (reached, changed)
    case List/Cons:
      (u, v) = pairs.head
      has_u = has_bit(reached, u)
      has_v = has_bit(reached, v)
      if has_u:
        if has_v:
          return scan_edges(pairs.tail, reached, changed)
        else:
          return scan_edges(pairs.tail, set_bit(reached, v), 1)
      else:
        if has_v:
          return scan_edges(pairs.tail, set_bit(reached, u), 1)
        else:
          return scan_edges(pairs.tail, reached, changed)

def closure(pairs, reversed_pairs, reached):
  (forward_reached, forward_changed) = scan_edges(pairs, reached, 0)
  if forward_changed == 0:
    return forward_reached
  else:
    (reverse_reached, reverse_changed) = scan_edges(reversed_pairs, forward_reached, 0)
    return closure(pairs, reversed_pairs, reverse_reached)

def members(i, reached, acc):
  if i == 0:
    return acc
  else:
    node = i - 1
    if has_bit(reached, node):
      return members(node, reached, List/Cons(node, acc))
    else:
      return members(node, reached, acc)
