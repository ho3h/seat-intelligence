def prog(x):
  (n, edges) = x
  matrix = make_matrix(n)
  matrix2 = add_edges(edges, matrix)
  matrix3 = add_diagonal(0, n, matrix2)
  closed = close_all(0, n, matrix3)
  return count_components(0, n, closed, 0)

def make_zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeros(n - 1))

def make_matrix(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(make_zeros(n), make_matrix(n - 1))

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

def add_edges(edges, matrix):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (u, v) = edges.head
      row = get_at(matrix, u)
      row2 = set_at(row, v, 1)
      matrix2 = set_at(matrix, u, row2)
      return add_edges(edges.tail, matrix2)

def add_diagonal(i, n, matrix):
  if i < n:
    row = get_at(matrix, i)
    row2 = set_at(row, i, 1)
    matrix2 = set_at(matrix, i, row2)
    return add_diagonal(i + 1, n, matrix2)
  else:
    return matrix

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
    if get_at(row, k) == 1:
      row2 = or_rows(row, row_k)
    else:
      row2 = row
    matrix2 = set_at(matrix, i, row2)
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

def has_prior_mutual(j, i, matrix, row_i):
  if j < i:
    row_j = get_at(matrix, j)
    if get_at(row_i, j) == 1:
      if get_at(row_j, i) == 1:
        return 1
      else:
        return has_prior_mutual(j + 1, i, matrix, row_i)
    else:
      return has_prior_mutual(j + 1, i, matrix, row_i)
  else:
    return 0

def count_components(i, n, matrix, acc):
  if i < n:
    row_i = get_at(matrix, i)
    if has_prior_mutual(0, i, matrix, row_i) == 1:
      return count_components(i + 1, n, matrix, acc)
    else:
      return count_components(i + 1, n, matrix, acc + 1)
  else:
    return acc
