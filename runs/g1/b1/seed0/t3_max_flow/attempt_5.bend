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
        if n <= 16:
          limit = 1 << n
          best = cut_search(0, limit, n, s, t, edges, (16777215, 16777215))
          (high, low) = best
          return low
        else:
          matrix = zero_matrix(n)
          adjacency = zero_adjacency(n)
          (matrix2, adjacency2) = load_graph(edges, matrix, adjacency, n)
          return flow_loop(matrix2, adjacency2, n, s, t, (0, 0))

def bit_set(mask, index):
  return (mask & (1 << index)) != 0

def cut_search(mask, limit, n, source, sink, edges, best):
  if mask == limit:
    return best
  else:
    if bit_set(mask, source):
      if bit_set(mask, sink):
        return cut_search(mask + 1, limit, n, source, sink, edges, best)
      else:
        capacity = cut_capacity(edges, mask, n, (0, 0))
        best2 = pair_min(best, capacity)
        return cut_search(mask + 1, limit, n, source, sink, edges, best2)
    else:
      return cut_search(mask + 1, limit, n, source, sink, edges, best)

def cut_capacity(edges, mask, n, total):
  match edges:
    case List/Nil:
      return total
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          if bit_set(mask, u):
            if bit_set(mask, v):
              return cut_capacity(edges.tail, mask, n, total)
            else:
              total2 = pair_add(total, (0, w))
              return cut_capacity(edges.tail, mask, n, total2)
          else:
            return cut_capacity(edges.tail, mask, n, total)
        else:
          return cut_capacity(edges.tail, mask, n, total)
      else:
        return cut_capacity(edges.tail, mask, n, total)

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

def zero_adjacency(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons([], zero_adjacency(n - 1))

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

def append_one(xs, value):
  match xs:
    case List/Nil:
      return List/Cons(value, List/Nil)
    case List/Cons:
      return List/Cons(xs.head, append_one(xs.tail, value))

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
    return h > 0
  else:
    return l > 0

def add_neighbor(xs, value):
  match xs:
    case List/Nil:
      return List/Cons(value, List/Nil)
    case List/Cons:
      return List/Cons(xs.head, add_neighbor(xs.tail, value))

def load_graph(edges, matrix, adjacency, n):
  match edges:
    case List/Nil:
      return (matrix, adjacency)
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          row = get_row(matrix, u)
          old = get_pair(row, v)
          updated = pair_add(old, (0, w))
          row2 = put_pair(row, v, updated)
          matrix2 = put_row(matrix, u, row2)

          adj_u = get_row(adjacency, u)
          adj_u2 = add_neighbor(adj_u, v)
          adjacency1 = put_row(adjacency, u, adj_u2)

          adj_v = get_row(adjacency1, v)
          adj_v2 = add_neighbor(adj_v, u)
          adjacency2 = put_row(adjacency1, v, adj_v2)

          return load_graph(edges.tail, matrix2, adjacency2, n)
        else:
          return load_graph(edges.tail, matrix, adjacency, n)
      else:
        return load_graph(edges.tail, matrix, adjacency, n)

def bfs_neighbors(matrix, adjacency, n, current, neighbors, pred, queue):
  match neighbors:
    case List/Nil:
      return (pred, queue)
    case List/Cons:
      v = neighbors.head
      capacity = get_pair(get_row(matrix, current), v)
      if pair_nonzero(capacity):
        if get_num(pred, v) == n:
          pred2 = put_num(pred, v, current)
          queue2 = append_one(queue, v)
          return bfs_neighbors(matrix, adjacency, n, current, neighbors.tail, pred2, queue2)
        else:
          return bfs_neighbors(matrix, adjacency, n, current, neighbors.tail, pred, queue)
      else:
        return bfs_neighbors(matrix, adjacency, n, current, neighbors.tail, pred, queue)

def bfs_loop(matrix, adjacency, n, sink, queue, pred):
  match queue:
    case List/Nil:
      return pred
    case List/Cons:
      current = queue.head
      if current == sink:
        return pred
      else:
        neighbors = get_row(adjacency, current)
        (pred2, queue2) = bfs_neighbors(matrix, adjacency, n, current, neighbors, pred, queue.tail)
        return bfs_loop(matrix, adjacency, n, sink, queue2, pred2)

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

def flow_loop(matrix, adjacency, n, source, sink, total):
  pred0 = filled_nums(n, n)
  pred1 = put_num(pred0, source, source)
  pred = bfs_loop(matrix, adjacency, n, sink, [source], pred1)
  if get_num(pred, sink) == n:
    (high, low) = total
    return low
  else:
    amount = bottleneck(sink, source, pred, matrix, (16777215, 16777215))
    matrix2 = augment_path(matrix, sink, source, pred, amount)
    total2 = pair_add(total, amount)
    return flow_loop(matrix2, adjacency, n, source, sink, total2)
