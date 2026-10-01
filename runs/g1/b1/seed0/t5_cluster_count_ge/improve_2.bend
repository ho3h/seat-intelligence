def prog(x):
  (n, k, pairs) = x
  chunks = (n + 23) / 24
  matrix = make_matrix(0, n, chunks, pairs)
  closed = close_all(matrix, 0, n)
  return count_components(closed, 0, n, k, 0)

def zero_words(i, chunks):
  if i == chunks:
    return []
  else:
    return List/Cons(0, zero_words(i + 1, chunks))

def set_word(words, i, mask):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, set_word(words.tail, i - 1, mask))

def add_edges(edges, node, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if u == node:
        row1 = set_word(row, v / 24, 1 << (v % 24))
        if v == node:
          row2 = set_word(row1, u / 24, 1 << (u % 24))
          return add_edges(edges.tail, node, row2)
        else:
          return add_edges(edges.tail, node, row1)
      else:
        if v == node:
          row1 = set_word(row, u / 24, 1 << (u % 24))
          return add_edges(edges.tail, node, row1)
        else:
          return add_edges(edges.tail, node, row)

def make_matrix(i, n, chunks, pairs):
  if i == n:
    return []
  else:
    empty = zero_words(0, chunks)
    row = set_word(empty, i / 24, 1 << (i % 24))
    row2 = add_edges(pairs, i, row)
    return List/Cons(row2, make_matrix(i + 1, n, chunks, pairs))

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def or_words(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(a.head | b.head, or_words(a.tail, b.tail))

def close_rows(rows, pivot, chunk, mask):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      word = at(rows.head, chunk)
      if (word & mask) != 0:
        row = or_words(rows.head, pivot)
        return List/Cons(row, close_rows(rows.tail, pivot, chunk, mask))
      else:
        return List/Cons(rows.head, close_rows(rows.tail, pivot, chunk, mask))

def close_all(matrix, p, n):
  if p == n:
    return matrix
  else:
    pivot = at(matrix, p)
    next_matrix = close_rows(matrix, pivot, p / 24, 1 << (p % 24))
    return close_all(next_matrix, p + 1, n)

def lower_nonzero(words, target, bit, i):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if i < target:
        if words.head != 0:
          return 1
        else:
          return lower_nonzero(words.tail, target, bit, i + 1)
      else:
        return (words.head % (1 << bit)) != 0

def count_word_bits(word, acc):
  if word == 0:
    return acc
  else:
    return count_word_bits(word >> 1, acc + (word & 1))

def count_bits(words, acc):
  match words:
    case List/Nil:
      return acc
    case List/Cons:
      bits = count_word_bits(words.head, 0)
      return count_bits(words.tail, acc + bits)

def count_components(matrix, i, n, k, acc):
  if i == n:
    return acc
  else:
    match matrix:
      case List/Nil:
        return acc
      case List/Cons:
        row = matrix.head
        has_lower = lower_nonzero(row, i / 24, i % 24, 0)
        if has_lower:
          return count_components(matrix.tail, i + 1, n, k, acc)
        else:
          if k <= 1:
            return count_components(matrix.tail, i + 1, n, k, acc + 1)
          else:
            size = count_bits(row, 0)
            if size >= k:
              return count_components(matrix.tail, i + 1, n, k, acc + 1)
            else:
              return count_components(matrix.tail, i + 1, n, k, acc)
