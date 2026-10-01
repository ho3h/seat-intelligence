def prog(x):
  (n, edges) = x
  blocks = (n + 23) / 24
  rows = make_rows(n, blocks)
  graph = build_graph(edges, rows)
  return count_u(graph, n, 0, 0)

def zero_list(k):
  if k == 0:
    return []
  else:
    tail = zero_list(k - 1)
    return List/Cons(0, tail)

def make_rows(n, blocks):
  if n == 0:
    return []
  else:
    row = zero_list(blocks)
    tail = make_rows(n - 1, blocks)
    return List/Cons(row, tail)

def get_row(rows, i):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return rows.head
      else:
        return get_row(rows.tail, i - 1)

def set_row(rows, i, value):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, rows.tail)
      else:
        tail = set_row(rows.tail, i - 1, value)
        return List/Cons(rows.head, tail)

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

def set_adj(rows, u, v):
  row = get_row(rows, u)
  block = v / 24
  bit = 1 << (v % 24)
  mask = get_mask(row, block)
  updated_row = set_mask(row, block, mask | bit)
  return set_row(rows, u, updated_row)

def add_edge(rows, u, v):
  forward = set_adj(rows, u, v)
  return set_adj(forward, v, u)

def build_graph(edges, rows):
  match edges:
    case List/Nil:
      return rows
    case List/Cons:
      (u, v) = edges.head
      updated = add_edge(rows, u, v)
      return build_graph(edges.tail, updated)

def has_bit(row, v):
  block = v / 24
  bit = 1 << (v % 24)
  mask = get_mask(row, block)
  return (mask & bit) != 0

def popcount24(x):
  a = x - ((x >> 1) & 5592405)
  b = (a & 3355443) + ((a >> 2) & 3355443)
  c = (b + (b >> 4)) & 986895
  d = c + (c >> 8)
  e = d + (d >> 16)
  return e & 63

def count_common(row_u, row_v, blocks, block, v, acc):
  if block >= blocks:
    return acc
  else:
    mask_u = get_mask(row_u, block)
    mask_v = get_mask(row_v, block)
    common = mask_u & mask_v
    if block == v / 24:
      offset = v % 24
      lower = (1 << (offset + 1)) - 1
      allowed = 16777215 - lower
      common = common & allowed
    else:
      common = common
    next_acc = acc + popcount24(common)
    return count_common(row_u, row_v, blocks, block + 1, v, next_acc)

def count_u(rows, n, u, acc):
  if u >= n:
    return acc
  else:
    row_u = get_row(rows, u)
    next_acc = count_v(rows, n, u, u + 1, row_u, acc)
    return count_u(rows, n, u + 1, next_acc)

def count_v(rows, n, u, v, row_u, acc):
  if v >= n:
    return acc
  else:
    if has_bit(row_u, v):
      row_v = get_row(rows, v)
      next_acc = count_common(row_u, row_v, (n + 23) / 24, v / 24, v, acc)
      return count_v(rows, n, u, v + 1, row_u, next_acc)
    else:
      return count_v(rows, n, u, v + 1, row_u, acc)
