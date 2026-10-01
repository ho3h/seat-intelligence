def prog(x):
  (n, edges) = x
  blocks = (n + 23) / 24
  rows = build_rows(0, n, edges, blocks)
  matrix = pack_rows(rows)
  closed = close_matrix(0, n, matrix, 0, 1)
  return count_chunks(closed) - n

def build_rows(i, n, edges, blocks):
  if i == n:
    return []
  else:
    initial = zero_blocks(blocks)
    initial = set_mark(initial, i)
    row = add_row_edges(edges, i, initial)
    rest = build_rows(i + 1, n, edges, blocks)
    return List/Cons(row, rest)

def add_row_edges(edges, source, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if u == source:
        return add_row_edges(edges.tail, source, set_mark(row, v))
      else:
        return add_row_edges(edges.tail, source, row)

def zero_blocks(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, zero_blocks(count - 1))

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

def pack_rows(rows):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      (chunk, rest) = take_rows(rows, 24)
      return List/Cons(chunk, pack_rows(rest))

def take_rows(rows, count):
  if count == 0:
    return ([], rows)
  else:
    match rows:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (front, rest) = take_rows(rows.tail, count - 1)
        return (List/Cons(rows.head, front), rest)

def chunk_at(chunks, index):
  match chunks:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return chunks.head
      else:
        return chunk_at(chunks.tail, index - 1)

def list_at(xs, index):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return list_at(xs.tail, index - 1)

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

def union_bits(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          head = a.head | b.head
          tail = union_bits(a.tail, b.tail)
          return List/Cons(head, tail)

def close_matrix(k, n, matrix, block, mask):
  if k == n:
    return matrix
  else:
    chunk = chunk_at(matrix, k / 24)
    pivot = list_at(chunk, k % 24)
    updated = close_chunks(matrix, pivot, block, mask)
    if k % 24 == 23:
      return close_matrix(k + 1, n, updated, block + 1, 1)
    else:
      return close_matrix(k + 1, n, updated, block, mask * 2)

def close_chunks(chunks, pivot, block, mask):
  match chunks:
    case List/Nil:
      return []
    case List/Cons:
      updated_chunk = close_chunk(chunks.head, pivot, block, mask)
      rest = close_chunks(chunks.tail, pivot, block, mask)
      return List/Cons(updated_chunk, rest)

def close_chunk(rows, pivot, block, mask):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if has_mark_block(rows.head, block, mask) == 1:
        row = union_bits(rows.head, pivot)
      else:
        row = rows.head
      rest = close_chunk(rows.tail, pivot, block, mask)
      return List/Cons(row, rest)

def count_chunks(chunks):
  match chunks:
    case List/Nil:
      return 0
    case List/Cons:
      return count_rows(chunks.head) + count_chunks(chunks.tail)

def count_rows(rows):
  match rows:
    case List/Nil:
      return 0
    case List/Cons:
      return count_bits(rows.head) + count_rows(rows.tail)

def count_bits(bits):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      return popcount24(bits.head) + count_bits(bits.tail)

def popcount24(x):
  a = x - ((x >> 1) & 5592405)
  b = (a & 3355443) + ((a >> 2) & 3355443)
  c = (b + (b >> 4)) & 986895
  return (c & 255) + ((c >> 8) & 255) + ((c >> 16) & 255)
