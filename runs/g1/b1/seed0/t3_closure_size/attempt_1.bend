def prog(x):
  (n, edges) = x
  adjacency = build_adjacency(0, n, edges)
  blocks = (n + 23) / 24
  return count_sources(0, n, adjacency, blocks, 0)

def build_adjacency(i, n, edges):
  if i == n:
    return []
  else:
    neighbors = collect_neighbors(edges, i, [])
    rest = build_adjacency(i + 1, n, edges)
    return List/Cons(neighbors, rest)

def collect_neighbors(edges, vertex, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == vertex:
        return collect_neighbors(edges.tail, vertex, List/Cons(v, acc))
      else:
        return collect_neighbors(edges.tail, vertex, acc)

def list_at(xs, index):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return list_at(xs.tail, index - 1)

def zero_blocks(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, zero_blocks(count - 1))

def has_mark(marks, vertex):
  block = vertex / 24
  offset = vertex % 24
  mask = 1 << offset
  return has_mark_block(marks, block, mask)

def has_mark_block(marks, block, mask):
  match marks:
    case List/Nil:
      return 0
    case List/Cons:
      if block == 0:
        if (marks.head & mask) != 0:
          return 1
        else:
          return 0
      else:
        return has_mark_block(marks.tail, block - 1, mask)

def set_mark(marks, vertex):
  block = vertex / 24
  offset = vertex % 24
  mask = 1 << offset
  return set_mark_block(marks, block, mask)

def set_mark_block(marks, block, mask):
  match marks:
    case List/Nil:
      return []
    case List/Cons:
      if block == 0:
        return List/Cons(marks.head | mask, marks.tail)
      else:
        return List/Cons(marks.head, set_mark_block(marks.tail, block - 1, mask))

def count_sources(source, n, adjacency, blocks, total):
  if source == n:
    return total
  else:
    marks = zero_blocks(blocks)
    marks = set_mark(marks, source)
    reachable = visit([source], marks, 0, adjacency)
    return count_sources(source + 1, n, adjacency, blocks, total + reachable)

def visit(stack, marks, count, adjacency):
  match stack:
    case List/Nil:
      return count
    case List/Cons:
      vertex = stack.head
      neighbors = list_at(adjacency, vertex)
      (next_stack, next_marks, next_count) = scan_neighbors(
        neighbors, stack.tail, marks, count
      )
      return visit(next_stack, next_marks, next_count, adjacency)

def scan_neighbors(neighbors, stack, marks, count):
  match neighbors:
    case List/Nil:
      return (stack, marks, count)
    case List/Cons:
      target = neighbors.head
      if has_mark(marks, target) == 0:
        next_marks = set_mark(marks, target)
        return scan_neighbors(
          neighbors.tail,
          List/Cons(target, stack),
          next_marks,
          count + 1
        )
      else:
        return scan_neighbors(neighbors.tail, stack, marks, count)
