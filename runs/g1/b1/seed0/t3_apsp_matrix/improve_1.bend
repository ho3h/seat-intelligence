def prog(x):
  (n, edges) = x
  matrix = init_rows(n, 0)
  matrix = apply_edges(matrix, edges)
  return floyd(matrix, n, 0)

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

def nth(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def floyd(matrix, n, k):
  if k == n:
    return matrix
  else:
    row_k = nth(matrix, k)
    changed = update_rows(matrix, row_k, k, 0)
    return floyd(changed, n, k + 1)

def update_rows(matrix, row_k, k, i):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if i == k:
        changed_row = matrix.head
      else:
        d_ik = nth(matrix.head, k)
        if d_ik == 16777215:
          changed_row = matrix.head
        else:
          changed_row = improve_row(matrix.head, row_k, d_ik)
      rest = update_rows(matrix.tail, row_k, k, i + 1)
      return List/Cons(changed_row, rest)

def improve_row(row, row_k, d_ik):
  match row:
    case List/Nil:
      return []
    case List/Cons:
      match row_k:
        case List/Nil:
          return []
        case List/Cons:
          old = row.head
          d_kj = row_k.head
          if d_kj == 16777215:
            value = old
          else:
            candidate = d_ik + d_kj
            if candidate < d_ik:
              value = old
            else:
              if candidate < old:
                value = candidate
              else:
                value = old
          rest = improve_row(row.tail, row_k.tail, d_ik)
          return List/Cons(value, rest)
