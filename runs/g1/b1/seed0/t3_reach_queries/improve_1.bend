def prog(x):
  (n, queries, edges) = x
  chunks = num_chunks(n)
  matrix = make_matrix(n, chunks, 0)
  matrix2 = add_edges(edges, matrix)
  closed = close_all(0, n, matrix2)
  return answer_queries(queries, closed, [])

def num_chunks(n):
  whole = n / 24
  if n % 24 == 0:
    return whole
  else:
    return whole + 1

def make_zero_chunks(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zero_chunks(n - 1))

def make_matrix(n, chunks, vertex):
  if vertex == n:
    return []
  else:
    row = bit_add(make_zero_chunks(chunks), vertex)
    return List/Cons(row, make_matrix(n, chunks, vertex + 1))

def bit_add(bits, vertex):
  index = vertex / 24
  mask = 1 << (vertex % 24)
  return update_chunk(bits, index, mask)

def update_chunk(bits, index, mask):
  match bits:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(bits.head | mask, bits.tail)
      else:
        return List/Cons(bits.head, update_chunk(bits.tail, index - 1, mask))

def bit_has(bits, vertex):
  chunk = get_chunk(bits, vertex / 24)
  mask = 1 << (vertex % 24)
  if chunk & mask == 0:
    return 0
  else:
    return 1

def get_chunk(bits, index):
  match bits:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return bits.head
      else:
        return get_chunk(bits.tail, index - 1)

def add_edges(edges, matrix):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (u, v) = edges.head
      matrix2 = add_edge(matrix, u, v)
      return add_edges(edges.tail, matrix2)

def add_edge(matrix, u, v):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if u == 0:
        row = bit_add(matrix.head, v)
        return List/Cons(row, matrix.tail)
      else:
        return List/Cons(matrix.head, add_edge(matrix.tail, u - 1, v))

def get_row(matrix, index):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return matrix.head
      else:
        return get_row(matrix.tail, index - 1)

def or_chunks(left, right):
  match left:
    case List/Nil:
      return []
    case List/Cons:
      match right:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(left.head | right.head, or_chunks(left.tail, right.tail))

def close_all(k, n, matrix):
  if k == n:
    return matrix
  else:
    pivot_row = get_row(matrix, k)
    matrix2 = close_rows(matrix, k, pivot_row)
    return close_all(k + 1, n, matrix2)

def close_rows(matrix, pivot, pivot_row):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if bit_has(matrix.head, pivot) == 1:
        row = or_chunks(matrix.head, pivot_row)
        return List/Cons(row, close_rows(matrix.tail, pivot, pivot_row))
      else:
        return List/Cons(matrix.head, close_rows(matrix.tail, pivot, pivot_row))

def answer_queries(queries, matrix, acc):
  match queries:
    case List/Nil:
      return reverse_list(acc)
    case List/Cons:
      (a, b) = queries.head
      row = get_row(matrix, a)
      answer = bit_has(row, b)
      return answer_queries(queries.tail, matrix, List/Cons(answer, acc))

def reverse_list(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
