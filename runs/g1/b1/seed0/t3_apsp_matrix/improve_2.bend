def prog(x):
  (n, edges) = x
  matrix = init_rows(n, 0)
  matrix = apply_edges(matrix, edges)
  if n <= 1:
    return matrix
  else:
    return square_until(matrix, n, 1, n - 1)

def init_rows(n, i):
  if i == n:
    return []
  else:
    row = init_row(n, i, 0)
    rest = init_rows(n, i + 1)
    return List/Cons(row, rest)

def init_row(n, i, j):
  if j == n:
    return []
  else:
    if i == j:
      value = 0
    else:
      value = 16777215
    rest = init_row(n, i, j + 1)
    return List/Cons(value, rest)

def apply_edges(matrix, edges):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (u, v, w) = edges.head
      changed = set_edge(matrix, u, v, w)
      return apply_edges(changed, edges.tail)

def set_edge(matrix, u, v, w):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if u == 0:
        changed_row = set_cell(matrix.head, v, w)
        return List/Cons(changed_row, matrix.tail)
      else:
        rest = set_edge(matrix.tail, u - 1, v, w)
        return List/Cons(matrix.head, rest)

def set_cell(row, v, w):
  match row:
    case List/Nil:
      return []
    case List/Cons:
      if v == 0:
        if w < row.head:
          return List/Cons(w, row.tail)
        else:
          return row
      else:
        rest = set_cell(row.tail, v - 1, w)
        return List/Cons(row.head, rest)

def square_until(matrix, n, covered, target):
  if covered >= target:
    return matrix
  else:
    transposed = transpose(matrix)
    squared = square_rows(matrix, transposed)
    return square_until(squared, n, covered * 2, target)

def transpose(matrix):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      return transpose_columns(matrix)

def transpose_columns(matrix):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      match matrix.head:
        case List/Nil:
          return []
        case List/Cons:
          column = take_heads(matrix)
          rest_matrix = drop_heads(matrix)
          rest_columns = transpose_columns(rest_matrix)
          return List/Cons(column, rest_columns)

def take_heads(matrix):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      match matrix.head:
        case List/Nil:
          return []
        case List/Cons:
          rest = take_heads(matrix.tail)
          return List/Cons(matrix.head.head, rest)

def drop_heads(matrix):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      match matrix.head:
        case List/Nil:
          return []
        case List/Cons:
          rest = drop_heads(matrix.tail)
          return List/Cons(matrix.head.tail, rest)

def square_rows(matrix, columns):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      new_row = square_row(matrix.head, columns)
      rest = square_rows(matrix.tail, columns)
      return List/Cons(new_row, rest)

def square_row(row, columns):
  match row:
    case List/Nil:
      return []
    case List/Cons:
      match columns:
        case List/Nil:
          return []
        case List/Cons:
          value = dot_min(row, columns.head, row.head)
          rest = square_row(row.tail, columns.tail)
          return List/Cons(value, rest)

def dot_min(left, right, best):
  match left:
    case List/Nil:
      return best
    case List/Cons:
      match right:
        case List/Nil:
          return best
        case List/Cons:
          a = left.head
          b = right.head
          if a == 16777215:
            next_best = best
          else:
            if b == 16777215:
              next_best = best
            else:
              candidate = a + b
              if candidate < a:
                next_best = best
              else:
                if candidate < best:
                  next_best = candidate
                else:
                  next_best = best
          return dot_min(left.tail, right.tail, next_best)
