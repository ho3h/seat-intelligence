def prog(x):
  (n, k, edges) = x
  if k == 0:
    return n
  else:
    adj = build_adjacency(n, 0, edges)
    full = n / 24
    rem = n % 24
    masks = make_full_masks(full)
    if rem == 0:
      active = masks
    else:
      active = append_last(masks, (1 << rem) - 1)
    return stabilize(adj, active, n, n, k)

def neighbors_for(v, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        return neighbors_for(v, edges.tail, List/Cons(b, acc))
      else:
        if b == v:
          return neighbors_for(v, edges.tail, List/Cons(a, acc))
        else:
          return neighbors_for(v, edges.tail, acc)

def build_adjacency(n, v, edges):
  if v == n:
    return []
  else:
    neighbors = neighbors_for(v, edges, [])
    rest = build_adjacency(n, v + 1, edges)
    return List/Cons(neighbors, rest)

def make_full_masks(count):
  if count == 0:
    return []
  else:
    return List/Cons(16777215, make_full_masks(count - 1))

def append_last(xs, value):
  match xs:
    case List/Nil:
      return List/Cons(value, [])
    case List/Cons:
      return List/Cons(xs.head, append_last(xs.tail, value))

def get_mask(masks, index):
  match masks:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return masks.head
      else:
        return get_mask(masks.tail, index - 1)

def is_active(v, masks):
  mask = get_mask(masks, v / 24)
  bit = 1 << (v % 24)
  if (mask & bit) == 0:
    return 0
  else:
    return 1

def count_active_neighbors(neighbors, masks, acc):
  match neighbors:
    case List/Nil:
      return acc
    case List/Cons:
      if is_active(neighbors.head, masks) == 1:
        return count_active_neighbors(neighbors.tail, masks, acc + 1)
      else:
        return count_active_neighbors(neighbors.tail, masks, acc)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def build_next(i, n, adjacency, active, k, chunk, out, kept):
  if i == n:
    if i % 24 == 0:
      return (reverse_list(out, []), kept)
    else:
      return (reverse_list(List/Cons(chunk, out), []), kept)
  else:
    match adjacency:
      case List/Nil:
        return (reverse_list(out, []), kept)
      case List/Cons:
        degree = count_active_neighbors(adjacency.head, active, 0)
        if degree >= k:
          next_chunk = chunk | (1 << (i % 24))
          next_kept = kept + 1
        else:
          next_chunk = chunk
          next_kept = kept
        if i % 24 == 23:
          return build_next(i + 1, n, adjacency.tail, active, k, 0, List/Cons(next_chunk, out), next_kept)
        else:
          return build_next(i + 1, n, adjacency.tail, active, k, next_chunk, out, next_kept)

def stabilize(adjacency, active, n, active_count, k):
  (next_active, next_count) = build_next(0, n, adjacency, active, k, 0, [], 0)
  if next_count == active_count:
    return next_count
  else:
    return stabilize(adjacency, next_active, n, next_count, k)
