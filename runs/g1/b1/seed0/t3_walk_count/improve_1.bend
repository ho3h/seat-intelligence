def prog(x):
  (n, s, t, k, edges) = x
  if s >= n:
    return 0
  else:
    if t >= n:
      return 0
    else:
      if k == 0:
        if s == t:
          return 1
        else:
          return 0
      else:
        e = edge_count(edges, 0)
        if e == 0:
          return 0
        else:
          bits = bit_count(k, 0)
          raw_limit = (n * n * bits) / e
          if raw_limit > 512:
            limit = 512
          else:
            limit = raw_limit
          if k <= limit:
            initial = init_vec(0, n, t)
            return walk_steps(k, n, s, edges, initial)
          else:
            zeros = make_zeros(n)
            (matrix, transposed) = build_matrices(0, n, edges)
            initial = init_vec(0, n, s)
            return power_walk(k, matrix, transposed, initial, t)

def edge_count(edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      return edge_count(edges.tail, acc + 1)

def bit_count(k, acc):
  if k == 0:
    return acc
  else:
    return bit_count(k / 2, acc + 1)

def make_zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zeros(n - 1))

def init_vec(i, n, target):
  if i == n:
    return []
  else:
    if i == target:
      return List/Cons(1, init_vec(i + 1, n, target))
    else:
      return List/Cons(0, init_vec(i + 1, n, target))

def walk_steps(rem, n, s, edges, vec):
  if rem == 0:
    return vec_get(vec, s)
  else:
    next_vec = build_vec(0, n, edges, vec)
    return walk_steps(rem - 1, n, s, edges, next_vec)

def build_vec(i, n, edges, vec):
  if i == n:
    return []
  else:
    count = sum_from(edges, i, vec, 0)
    return List/Cons(count, build_vec(i + 1, n, edges, vec))

def sum_from(edges, src, vec, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        count = vec_get(vec, v)
        return sum_from(edges.tail, src, vec, acc + count)
      else:
        return sum_from(edges.tail, src, vec, acc)

def vec_get(vec, idx):
  match vec:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return vec.head
      else:
        return vec_get(vec.tail, idx - 1)

def build_matrices(i, n, edges):
  if i == n:
    return ([], [])
  else:
    zeros = make_zeros(n)
    row = fill_forward(edges, i, n, zeros)
    col = fill_reverse(edges, i, n, zeros)
    (rows_tail, cols_tail) = build_matrices(i + 1, n, edges)
    return (List/Cons(row, rows_tail), List/Cons(col, cols_tail))

def fill_forward(edges, src, n, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        if v < n:
          updated = increment_at(row, v)
          return fill_forward(edges.tail, src, n, updated)
        else:
          return fill_forward(edges.tail, src, n, row)
      else:
        return fill_forward(edges.tail, src, n, row)

def fill_reverse(edges, dst, n, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if v == dst:
        if u < n:
          updated = increment_at(row, u)
          return fill_reverse(edges.tail, dst, n, updated)
        else:
          return fill_reverse(edges.tail, dst, n, row)
      else:
        return fill_reverse(edges.tail, dst, n, row)

def increment_at(xs, idx):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, increment_at(xs.tail, idx - 1))

def dot_product(xs, ys):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return xs.head * ys.head + dot_product(xs.tail, ys.tail)

def product_row(row, cols):
  match cols:
    case List/Nil:
      return []
    case List/Cons:
      value = dot_product(row, cols.head)
      return List/Cons(value, product_row(row, cols.tail))

def matrix_product(rows, cols):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      row = product_row(rows.head, cols)
      return List/Cons(row, matrix_product(rows.tail, cols))

def vector_product(vec, cols):
  match cols:
    case List/Nil:
      return []
    case List/Cons:
      value = dot_product(vec, cols.head)
      return List/Cons(value, vector_product(vec, cols.tail))

def power_walk(k, matrix, transposed, vec, target):
  if k == 0:
    return vec_get(vec, target)
  else:
    if k % 2 == 1:
      next_vec = vector_product(vec, transposed)
    else:
      next_vec = vec
    half = k / 2
    if half == 0:
      return vec_get(next_vec, target)
    else:
      next_matrix = matrix_product(matrix, transposed)
      next_transposed = matrix_product(transposed, matrix)
      return power_walk(half, next_matrix, next_transposed, next_vec, target)
