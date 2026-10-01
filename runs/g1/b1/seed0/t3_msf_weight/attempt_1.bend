def prog(x):
  (n, edges) = x
  seen = make_zeroes((n + 23) / 24)
  return process_vertices(0, n, edges, seen, 0)

def make_zeroes(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeroes(n - 1))

def list_get(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_get(xs.tail, i - 1)

def list_put(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, list_put(xs.tail, i - 1, value))

def is_seen(seen, idx):
  value = list_get(seen, idx / 24)
  mask = 1 << (idx % 24)
  if (value & mask) != 0:
    return 1
  else:
    return 0

def mark_seen(seen, idx):
  block = idx / 24
  value = list_get(seen, block)
  mask = 1 << (idx % 24)
  return list_put(seen, block, value | mask)

def pick_vertex(seen_u, u, v):
  if seen_u == 1:
    return v
  else:
    return u

def find_min(edges, seen, has, bestw, bestv):
  match edges:
    case List/Nil:
      return (has, bestw, bestv)
    case List/Cons:
      (u, v, w) = edges.head
      seen_u = is_seen(seen, u)
      seen_v = is_seen(seen, v)
      if seen_u != seen_v:
        candidate = pick_vertex(seen_u, u, v)
        if has == 0:
          return find_min(edges.tail, seen, 1, w, candidate)
        else:
          if w < bestw:
            return find_min(edges.tail, seen, 1, w, candidate)
          else:
            return find_min(edges.tail, seen, has, bestw, bestv)
      else:
        return find_min(edges.tail, seen, has, bestw, bestv)

def grow_component(edges, seen, total):
  (has, bestw, bestv) = find_min(edges, seen, 0, 0, 0)
  if has == 0:
    return (seen, total)
  else:
    seen2 = mark_seen(seen, bestv)
    return grow_component(edges, seen2, total + bestw)

def process_vertices(i, n, edges, seen, total):
  if i == n:
    return total
  else:
    if is_seen(seen, i) == 1:
      return process_vertices(i + 1, n, edges, seen, total)
    else:
      seen1 = mark_seen(seen, i)
      (seen2, total2) = grow_component(edges, seen1, total)
      return process_vertices(i + 1, n, edges, seen2, total2)
