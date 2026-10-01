def prog(x):
  (n, edges) = x
  blocks = (n + 23) / 24
  rows = make_rows(n, blocks, edges, 0)
  return count_triangles(rows, blocks, 0)

def zero_list(k):
  if k == 0:
    return []
  else:
    tail = zero_list(k - 1)
    return List/Cons(0, tail)

def get_mask(row, i):
  match row:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return row.head
      else:
        return get_mask(row.tail, i - 1)

def set_mask(row, i, value):
  match row:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, row.tail)
      else:
        tail = set_mask(row.tail, i - 1, value)
        return List/Cons(row.head, tail)

def add_neighbor(row, neighbor):
  block = neighbor / 24
  bit = 1 << (neighbor % 24)
  mask = get_mask(row, block)
  return set_mask(row, block, mask | bit)

def build_row(edges, vertex, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (a, b) = edges.head
      if a == vertex:
        updated = add_neighbor(row, b)
      else:
        updated = row
      if b == vertex:
        updated2 = add_neighbor(updated, a)
      else:
        updated2 = updated
      return build_row(edges.tail, vertex, updated2)

def make_rows(n, blocks, edges, vertex):
  if vertex >= n:
    return []
  else:
    row = build_row(edges, vertex, zero_list(blocks))
    tail = make_rows(n, blocks, edges, vertex + 1)
    return List/Cons(row, tail)

def has_bit(row, vertex):
  block = vertex / 24
  bit = 1 << (vertex % 24)
  mask = get_mask(row, block)
  return (mask & bit) != 0

def popcount24(x):
  a = x - ((x >> 1) & 5592405)
  b = (a & 3355443) + ((a >> 2) & 3355443)
  c = (b + (b >> 4)) & 986895
  d = c + (c >> 8)
  e = d + (d >> 16)
  return e & 63

def count_common(row_u, row_v, block, first_block, vertex, acc):
  match row_u:
    case List/Nil:
      return acc
    case List/Cons:
      match row_v:
        case List/Nil:
          return acc
        case List/Cons:
          if block < first_block:
            return count_common(row_u.tail, row_v.tail, block + 1, first_block, vertex, acc)
          else:
            common = row_u.head & row_v.head
            if block == first_block:
              offset = vertex % 24
              lower = (1 << (offset + 1)) - 1
              allowed = 16777215 - lower
              common2 = common & allowed
            else:
              common2 = common
            next_acc = acc + popcount24(common2)
            return count_common(row_u.tail, row_v.tail, block + 1, first_block, vertex, next_acc)

def count_later(rows, row_u, vertex, acc):
  match rows:
    case List/Nil:
      return acc
    case List/Cons:
      if has_bit(row_u, vertex):
        common = count_common(row_u, rows.head, 0, vertex / 24, vertex, 0)
        next_acc = acc + common
      else:
        next_acc = acc
      return count_later(rows.tail, row_u, vertex + 1, next_acc)

def count_triangles(rows, blocks, vertex):
  match rows:
    case List/Nil:
      return 0
    case List/Cons:
      contribution = count_later(rows.tail, rows.head, vertex + 1, 0)
      remaining = count_triangles(rows.tail, blocks, vertex + 1)
      return contribution + remaining
