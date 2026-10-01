def prog(inp):
  (n, x, pairs) = inp
  block_count = (n + 23) / 24
  masks = zero_masks(block_count)
  masks2 = set_node(masks, x)
  return repeat_scans(pairs, masks2, x)

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

def repeat_scans(pairs, masks, best):
  (masks2, best2, added) = scan_edges(pairs, masks, best, 0)
  if added == 0:
    return best2
  else:
    return repeat_scans(pairs, masks2, best2)

def scan_edges(pairs, masks, best, added):
  match pairs:
    case List/Nil:
      return (masks, best, added)
    case List/Cons:
      (u, v) = pairs.head
      if marked(masks, u):
        if marked(masks, v):
          return scan_edges(pairs.tail, masks, best, added)
        else:
          masks2 = set_node(masks, v)
          best2 = larger(best, v)
          return scan_edges(pairs.tail, masks2, best2, 1)
      else:
        if marked(masks, v):
          masks2 = set_node(masks, u)
          best2 = larger(best, u)
          return scan_edges(pairs.tail, masks2, best2, 1)
        else:
          return scan_edges(pairs.tail, masks, best, added)
