def prog(x):
  (n, s, t, edges) = x
  if s == t:
    return 0
  else:
    if s >= n:
      return 0
    else:
      if t >= n:
        return 0
      else:
        matrix = zero_matrix(n)
        matrix2 = load_edges(edges, matrix, n)
        return flow_loop(matrix2, n, s, t, (0, 0))

def zero_pairs(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons((0, 0), zero_pairs(n - 1))

def zero_matrix(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(zero_pairs(n), zero_matrix(n - 1))

def filled_nums(n, value):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(value, filled_nums(n - 1, value))

def get_num(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_num(xs.tail, i - 1)

def put_num(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, put_num(xs.tail, i - 1, value))

def get_pair(xs, i):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_pair(xs.tail, i - 1)

def put_pair(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, put_pair(xs.tail, i - 1, value))

def get_row(matrix, i):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return matrix.head
        case _:
          return get_row(matrix.tail, i - 1)

def put_row(matrix, i, row):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(row, matrix.tail)
        case _:
          return List/Cons(matrix.head, put_row(matrix.tail, i - 1, row))

def pair_add(a, b):
  (ah, al) = a
  (bh, bl) = b
  if al > 16777215 - bl:
    return (ah + bh + 1, al + bl)
  else:
    return (ah + bh, al + bl)

def pair_sub(a, b):
  (ah, al) = a
  (bh, bl) = b
  if al >= bl:
    return (ah - bh, al - bl)
  else:
    return (ah - bh - 1, al - bl)

def pair_min(a, b):
  (ah, al) = a
  (bh, bl) = b
  if ah < bh:
    return a
  else:
    if ah > bh:
      return b
    else:
      if al < bl:
        return a
      else:
        return b

def pair_nonzero(a):
  (h, l) = a
  if h > 0:
    return True
  else:
    return l > 0

def load_edges(edges, matrix, n):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          row = get_row(matrix, u)
          old = get_pair(row, v)
          updated = pair_add(old, (0, w))
          row2 = put_pair(row, v, updated)
          matrix2 = put_row(matrix, u, row2)
          return load_edges(edges.tail, matrix2, n)
        else:
          return load_edges(edges.tail, matrix, n)
      else:
        return load_edges(edges.tail, matrix, n)

def dfs_scan(matrix, n, current, sink, j, pred):
  switch j:
    case 0:
      return (0, pred)
    case _:
      v = j - 1
      capacity = get_pair(get_row(matrix, current), v)
      if pair_nonzero(capacity):
        if get_num(pred, v) == n:
          pred2 = put_num(pred, v, current)
          (found, pred3) = dfs_visit(matrix, n, v, sink, pred2)
          if found == 1:
            return (1, pred3)
          else:
            return dfs_scan(matrix, n, current, sink, j - 1, pred3)
        else:
          return dfs_scan(matrix, n, current, sink, j - 1, pred)
      else:
        return dfs_scan(matrix, n, current, sink, j - 1, pred)

def dfs_visit(matrix, n, current, sink, pred):
  if current == sink:
    return (1, pred)
  else:
    return dfs_scan(matrix, n, current, sink, n, pred)

def bottleneck(current, source, pred, matrix, acc):
  if current == source:
    return acc
  else:
    previous = get_num(pred, current)
    capacity = get_pair(get_row(matrix, previous), current)
    smaller = pair_min(acc, capacity)
    return bottleneck(previous, source, pred, matrix, smaller)

def augment_path(matrix, current, source, pred, amount):
  if current == source:
    return matrix
  else:
    previous = get_num(pred, current)
    forward = get_pair(get_row(matrix, previous), current)
    backward = get_pair(get_row(matrix, current), previous)
    forward2 = pair_sub(forward, amount)
    backward2 = pair_add(backward, amount)
    row1 = put_pair(get_row(matrix, previous), current, forward2)
    matrix1 = put_row(matrix, previous, row1)
    row2 = put_pair(get_row(matrix1, current), previous, backward2)
    matrix2 = put_row(matrix1, current, row2)
    return augment_path(matrix2, previous, source, pred, amount)

def flow_loop(matrix, n, source, sink, total):
  pred0 = filled_nums(n, n)
  pred1 = put_num(pred0, source, source)
  (found, pred) = dfs_visit(matrix, n, source, sink, pred1)
  if found == 0:
    (high, low) = total
    return low
  else:
    amount = bottleneck(sink, source, pred, matrix, (16777215, 16777215))
    matrix2 = augment_path(matrix, sink, source, pred, amount)
    total2 = pair_add(total, amount)
    return flow_loop(matrix2, n, source, sink, total2)
