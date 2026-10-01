def prog(x):
  (n, s, edges) = x
  chunks = (n + 23) / 24
  rows = build_rows(n, 0, edges, chunks)
  rounds = rounds_needed(n, 1)
  closed = square_rounds(rows, rounds)
  return count_bits(get_row(closed, s))

def build_rows(count, index, edges, chunks):
  switch count:
    case 0:
      return []
    case _:
      empty = zero_chunks(chunks)
      identity_row = set_bit(empty, index)
      row = add_row_edges(edges, index, identity_row)
      rest = build_rows(count - 1, index + 1, edges, chunks)
      return List/Cons(row, rest)

def add_row_edges(edges, index, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if u == index:
        row2 = set_bit(row, v)
        return add_row_edges(edges.tail, index, row2)
      else:
        return add_row_edges(edges.tail, index, row)

def zero_chunks(count):
  switch count:
    case 0:
      return []
    case _:
      return List/Cons(0, zero_chunks(count - 1))

def rounds_needed(n, power):
  if power >= n:
    return 0
  else:
    return 1 + rounds_needed(n, power * 2)

def square_rounds(rows, rounds):
  switch rounds:
    case 0:
      return rows
    case _:
      squared = square_all(rows, rows)
      return square_rounds(squared, rounds - 1)

def square_all(rows, old_rows):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      row = square_row(rows.head, old_rows, 0, rows.head)
      rest = square_all(rows.tail, old_rows)
      return List/Cons(row, rest)

def square_row(base, rows, index, acc):
  match rows:
    case List/Nil:
      return acc
    case List/Cons:
      if is_set(base, index) == 1:
        acc2 = union_bits(acc, rows.head)
        return square_row(base, rows.tail, index + 1, acc2)
      else:
        return square_row(base, rows.tail, index + 1, acc)

def union_bits(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          value = a.head | b.head
          rest = union_bits(a.tail, b.tail)
          return List/Cons(value, rest)

def get_row(rows, index):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      switch index:
        case 0:
          return rows.head
        case _:
          return get_row(rows.tail, index - 1)

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
          rest = set_at(xs.tail, index - 1, value)
          return List/Cons(xs.head, rest)

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

def count_bits(bits):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      return popcount(bits.head) + count_bits(bits.tail)

def popcount(value):
  switch value:
    case 0:
      return 0
    case _:
      return (value & 1) + popcount(value >> 1)
