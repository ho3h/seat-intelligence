def prog(x):
  (n, s, edges) = x
  empty = zero_chunks((n + 23) / 24)
  seen = set_bit(empty, s)
  return bfs(edges, seen, seen, 1)

def bfs(edges, active, seen, total):
  empty = zero_chunks(size_chunks(seen))
  (seen2, next_active, added, total2) = scan_edges(edges, active, seen, empty, 0, total)
  if added == 0:
    return total2
  else:
    return bfs(edges, next_active, seen2, total2)

def scan_edges(edges, active, seen, next_active, added, total):
  match edges:
    case List/Nil:
      return (seen, next_active, added, total)
    case List/Cons:
      (u, v) = edges.head
      if is_set(active, u) == 1:
        if is_set(seen, v) == 0:
          seen2 = set_bit(seen, v)
          next2 = set_bit(next_active, v)
          return scan_edges(edges.tail, active, seen2, next2, added + 1, total + 1)
        else:
          return scan_edges(edges.tail, active, seen, next_active, added, total)
      else:
        return scan_edges(edges.tail, active, seen, next_active, added, total)

def zero_chunks(k):
  switch k:
    case 0:
      return []
    case _:
      return List/Cons(0, zero_chunks(k - 1))

def size_chunks(bits):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + size_chunks(bits.tail)

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch index:
        case 0:
          return xs.head
        case _:
          return get_at(xs.tail, index - 1)

def set_at(xs, index, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch index:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, set_at(xs.tail, index - 1, value))

def set_bit(bits, vertex):
  index = vertex / 24
  mask = 1 << (vertex % 24)
  value = get_at(bits, index) | mask
  return set_at(bits, index, value)

def is_set(bits, vertex):
  index = vertex / 24
  mask = 1 << (vertex % 24)
  value = get_at(bits, index)
  if (value & mask) == 0:
    return 0
  else:
    return 1
