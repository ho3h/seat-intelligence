def prog(x):
  (n, edges) = x
  chunks = (n + 23) / 24
  matrix = make_matrix(n, chunks)
  matrix2 = add_edges(edges, matrix)
  closed = close_all(0, n, matrix2)
  return count_components(0, n, closed, [], 0)

def make_zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeros(n - 1))

def make_matrix(n, chunks):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(make_zeros(chunks), make_matrix(n - 1, chunks))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def has_bit(bits, v):
  word = get_at(bits, v / 24)
  bit = 1 << (v % 24)
  if (word & bit) != 0:
    return 1
  else:
    return 0

def set_bit(bits, v):
  word_index = v / 24
  offset = v % 24
  word = get_at(bits, word_index)
  bit = 1 << offset
  return set_at(bits, word_index, word | bit)

def add_edges(edges, matrix):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (u, v) = edges.head
      row = get_at(matrix, u)
      row2 = set_bit(row, v)
      matrix2 = set_at(matrix, u, row2)
      return add_edges(edges.tail, matrix2)

def or_rows(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(a.head | b.head, or_rows(a.tail, b.tail))

def update_rows(i, n, k, row_k, matrix):
  if i < n:
    row = get_at(matrix, i)
    if has_bit(row, k) == 1:
      row2 = or_rows(row, row_k)
      matrix2 = set_at(matrix, i, row2)
    else:
      matrix2 = matrix
    return update_rows(i + 1, n, k, row_k, matrix2)
  else:
    return matrix

def close_all(k, n, matrix):
  if k < n:
    row_k = get_at(matrix, k)
    matrix2 = update_rows(0, n, k, row_k, matrix)
    return close_all(k + 1, n, matrix2)
  else:
    return matrix

def has_prior_mutual(prior, j, i, curr):
  match prior:
    case List/Nil:
      return 0
    case List/Cons:
      if has_bit(curr, j) == 1:
        if has_bit(prior.head, i) == 1:
          return 1
        else:
          return has_prior_mutual(prior.tail, j - 1, i, curr)
      else:
        return has_prior_mutual(prior.tail, j - 1, i, curr)

def count_components(i, n, matrix, prior, acc):
  if i == n:
    return acc
  else:
    match matrix:
      case List/Nil:
        return acc
      case List/Cons:
        curr = matrix.head
        if has_prior_mutual(prior, i - 1, i, curr) == 1:
          return count_components(i + 1, n, matrix.tail, List/Cons(curr, prior), acc)
        else:
          return count_components(i + 1, n, matrix.tail, List/Cons(curr, prior), acc + 1)
