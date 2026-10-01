def prog(inp):
  (n, x, pairs) = inp
  block_count = (n + 23) / 24
  masks = zero_masks(block_count)
  masks = set_node(masks, x)
  return explore([x], masks, x, pairs)

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

def explore(todo, masks, best, pairs):
  match todo:
    case List/Nil:
      return best
    case List/Cons:
      (todo2, masks2, best2) = scan_edges(pairs, todo.head, masks, todo.tail, best)
      return explore(todo2, masks2, best2, pairs)

def scan_edges(pairs, cur, masks, todo, best):
  match pairs:
    case List/Nil:
      return (todo, masks, best)
    case List/Cons:
      (u, v) = pairs.head
      if cur == u:
        if marked(masks, v):
          return scan_edges(pairs.tail, cur, masks, todo, best)
        else:
          masks2 = set_node(masks, v)
          todo2 = List/Cons(v, todo)
          best2 = larger(best, v)
          return scan_edges(pairs.tail, cur, masks2, todo2, best2)
      else:
        if cur == v:
          if marked(masks, u):
            return scan_edges(pairs.tail, cur, masks, todo, best)
          else:
            masks2 = set_node(masks, u)
            todo2 = List/Cons(u, todo)
            best2 = larger(best, u)
            return scan_edges(pairs.tail, cur, masks2, todo2, best2)
        else:
          return scan_edges(pairs.tail, cur, masks, todo, best)
