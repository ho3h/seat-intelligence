def prog(inp):
  (n, x, pairs) = inp
  block_count = (n + 23) / 24
  masks = zero_masks(block_count)
  masks2 = set_node(masks, x)
  reversed_pairs = reverse_list(pairs)
  return explore(pairs, reversed_pairs, masks2, x, n - 1, 0)

def zero_masks(k):
  switch k:
    case 0:
      return []
    case _:
      return List/Cons(0, zero_masks(k - 1))

def get_mask(masks, idx):
  match masks:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return masks.head
      else:
        return get_mask(masks.tail, idx - 1)

def set_mask(masks, idx, bit):
  match masks:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(masks.head | bit, masks.tail)
      else:
        return List/Cons(masks.head, set_mask(masks.tail, idx - 1, bit))

def set_node(masks, node):
  idx = node / 24
  bit = 1 << (node % 24)
  return set_mask(masks, idx, bit)

def marked(masks, node):
  idx = node / 24
  bit = 1 << (node % 24)
  mask = get_mask(masks, idx)
  return (mask & bit) != 0

def larger(a, b):
  if a > b:
    return a
  else:
    return b

def reverse_list(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def explore(pairs, reversed_pairs, masks, best, target, direction):
  if best == target:
    return best
  else:
    if direction == 0:
      (masks2, best2, added) = scan_edges(pairs, masks, best, target, 0)
    else:
      (masks2, best2, added) = scan_edges(reversed_pairs, masks, best, target, 0)
    if added == 0:
      return best2
    else:
      if best2 == target:
        return best2
      else:
        if direction == 0:
          return explore(pairs, reversed_pairs, masks2, best2, target, 1)
        else:
          return explore(pairs, reversed_pairs, masks2, best2, target, 0)

def scan_edges(pairs, masks, best, target, added):
  if best == target:
    return (masks, best, added)
  else:
    match pairs:
      case List/Nil:
        return (masks, best, added)
      case List/Cons:
        (u, v) = pairs.head
        if marked(masks, u):
          if marked(masks, v):
            return scan_edges(pairs.tail, masks, best, target, added)
          else:
            masks2 = set_node(masks, v)
            best2 = larger(best, v)
            return scan_edges(pairs.tail, masks2, best2, target, 1)
        else:
          if marked(masks, v):
            masks2 = set_node(masks, u)
            best2 = larger(best, u)
            return scan_edges(pairs.tail, masks2, best2, target, 1)
          else:
            return scan_edges(pairs.tail, masks, best, target, added)
