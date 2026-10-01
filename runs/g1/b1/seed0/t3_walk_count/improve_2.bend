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
        m = edge_count(edges, 0)
        if m == 0:
          return 0
        else:
          bits = bit_count(k, 0)
          threshold = n * bits
          if m < n:
            if k <= threshold:
              initial = init_vec(0, n, s)
              return scatter_walk(k, n, edges, initial, t)
            else:
              (matrix, transposed) = build_matrices(0, n, edges)
              initial = init_vec(0, n, s)
              return power_walk(k, matrix, transposed, initial, t)
          else:
            if k <= threshold:
              columns = build_columns(0, n, edges)
              initial = init_vec(0, n, s)
              return linear_walk(k, columns, initial, t)
            else:
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

def init_vec(i, n, start):
  if i == n:
    return []
  else:
    if i == start:
      return List/Cons(1, init_vec(i + 1, n, start))
    else:
      return List/Cons(0, init_vec(i + 1, n, start))

def make_zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zeros(n - 1))

def vec_get(vec, idx):
  match vec:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return vec.head
      else:
        return vec_get(vec.tail, idx - 1)

def increment_by(xs, idx, amount):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(xs.head + amount, xs.tail)
      else:
        return List/Cons(xs.head, increment_by(xs.tail, idx - 1, amount))

def scatter_walk(rem, n, edges, vec, target):
  if rem == 0:
    return vec_get(vec, target)
  else:
    next_vec = scatter_edges(edges, n, vec, make_zeros(n))
    return scatter_walk(rem - 1, n, edges, next_vec, target)

def scatter_edges(edges, n, vec, out):
  match edges:
    case List/Nil:
      return out
    case List/Cons:
      (u, v) = edges.head
      if u < n:
        if v < n:
          amount = vec_get(vec, u)
          updated = increment_by(out, v, amount)
          return scatter_edges(edges.tail, n, vec, updated)
        else:
          return scatter_edges(edges.tail, n, vec, out)
      else:
        return scatter_edges(edges.tail, n, vec, out)

def build_columns(i, n, edges):
  if i == n:
    return []
  else:
    zeros = make_zeros(n)
    column = fill_reverse(edges, i, n, zeros)
    return List/Cons(column, build_columns(i + 1, n, edges))

def fill_reverse(edges, dst, n, column):
  match edges:
    case List/Nil:
      return column
    case List/Cons:
      (u, v) = edges.head
      if v == dst:
        if u < n:
          updated = increment_by(column, u, 1)
          return fill_reverse(edges.tail, dst, n, updated)
        else:
          return fill_reverse(edges.tail, dst, n, column)
      else:
        return fill_reverse(edges.tail, dst, n, column)

def dot_product(xs, ys):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return xs.head * ys.head + dot_product(xs.tail, ys.tail)

def vector_product(vec, columns):
  match columns:
    case List/Nil:
      return []
    case List/Cons:
      value = dot_product(vec, columns.head)
      return List/Cons(value, vector_product(vec, columns.tail))

def linear_walk(rem, columns, vec, target):
  if rem == 0:
    return vec_get(vec, target)
  else:
    next_vec = vector_product(vec, columns)
    return linear_walk(rem - 1, columns, next_vec, target)

def fill_forward(edges, src, n, row):
  match edges:
    case List/Nil:
      return row
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        if v < n:
          updated = increment_by(row, v, 1)
          return fill_forward(edges.tail, src, n, updated)
        else:
          return fill_forward(edges.tail, src, n, row)
      else:
        return fill_forward(edges.tail, src, n, row)

def build_matrices(i, n, edges):
  if i == n:
    return ([], [])
  else:
    zeros = make_zeros(n)
    row = fill_forward(edges, i, n, zeros)
    column = fill_reverse(edges, i, n, make_zeros(n))
    (rows_tail, columns_tail) = build_matrices(i + 1, n, edges)
    return (List/Cons(row, rows_tail), List/Cons(column, columns_tail))

def product_row(row, columns):
  match columns:
    case List/Nil:
      return []
    case List/Cons:
      value = dot_product(row, columns.head)
      return List/Cons(value, product_row(row, columns.tail))

def matrix_product(rows, columns):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      product = product_row(rows.head, columns)
      return List/Cons(product, matrix_product(rows.tail, columns))

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
