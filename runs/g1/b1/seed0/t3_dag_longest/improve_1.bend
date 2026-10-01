def prog(x):
  (n, edges) = x
  size = tree_size(n, 1)
  tree = build_tree(size)
  tree = build_graph(edges, tree, size)
  queue = find_sources(0, n, tree, size, [])
  tree = process_queue(queue, tree, size)
  return max_distance(0, n, tree, size, 0)

def tree_size(n, size):
  if size < n:
    return tree_size(n, size * 2)
  else:
    return size

def build_tree(size):
  if size == 1:
    return ([], 0, 0)
  else:
    half = size / 2
    return (build_tree(half), build_tree(half))

def tree_get(tree, index, size):
  if size == 1:
    return tree
  else:
    half = size / 2
    (left, right) = tree
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def tree_set(tree, index, size, value):
  if size == 1:
    return value
  else:
    half = size / 2
    (left, right) = tree
    if index < half:
      return (tree_set(left, index, half, value), right)
    else:
      return (left, tree_set(right, index - half, half, value))

def build_graph(edges, tree, size):
  match edges:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v) = edges.head
      (adj_u, degree_u, distance_u) = tree_get(tree, u, size)
      tree = tree_set(tree, u, size, (List/Cons(v, adj_u), degree_u, distance_u))
      (adj_v, degree_v, distance_v) = tree_get(tree, v, size)
      tree = tree_set(tree, v, size, (adj_v, degree_v + 1, distance_v))
      return build_graph(edges.tail, tree, size)

def find_sources(i, n, tree, size, queue):
  if i == n:
    return queue
  else:
    (adj, degree, distance) = tree_get(tree, i, size)
    if degree == 0:
      return find_sources(i + 1, n, tree, size, List/Cons(i, queue))
    else:
      return find_sources(i + 1, n, tree, size, queue)

def process_queue(queue, tree, size):
  match queue:
    case List/Nil:
      return tree
    case List/Cons:
      u = queue.head
      (adj, degree, distance) = tree_get(tree, u, size)
      (tree, next_queue) = process_neighbors(adj, distance, tree, size, queue.tail)
      return process_queue(next_queue, tree, size)

def process_neighbors(neighbors, source_distance, tree, size, queue):
  match neighbors:
    case List/Nil:
      return (tree, queue)
    case List/Cons:
      v = neighbors.head
      (adj, degree, distance) = tree_get(tree, v, size)
      next_degree = degree - 1
      candidate = source_distance + 1
      if candidate > distance:
        next_distance = candidate
      else:
        next_distance = distance
      tree = tree_set(tree, v, size, (adj, next_degree, next_distance))
      if next_degree == 0:
        queue = List/Cons(v, queue)
      else:
        queue = queue
      return process_neighbors(neighbors.tail, source_distance, tree, size, queue)

def max_distance(i, n, tree, size, current):
  if i == n:
    return current
  else:
    (adj, degree, distance) = tree_get(tree, i, size)
    if distance > current:
      return max_distance(i + 1, n, tree, size, distance)
    else:
      return max_distance(i + 1, n, tree, size, current)
