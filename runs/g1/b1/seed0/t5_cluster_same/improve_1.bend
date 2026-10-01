def prog(x):
  (n, pairs, queries) = x
  capacity = tree_capacity(n, 1)
  (parents, sizes) = build_trees(capacity, 0, n)
  (parents2, sizes2) = merge_edges(pairs, parents, sizes, capacity)
  return answer_queries(queries, parents2, capacity)

def tree_capacity(n, size):
  if size >= n:
    return size
  else:
    return tree_capacity(n, size * 2)

def build_trees(size, base, n):
  if size == 1:
    if base < n:
      return ((0, base, 0), (0, 1, 0))
    else:
      return ((0, 0, 0), (0, 0, 0))
  else:
    half = size / 2
    (left_parents, left_sizes) = build_trees(half, base, n)
    (right_parents, right_sizes) = build_trees(half, base + half, n)
    return ((1, left_parents, right_parents), (1, left_sizes, right_sizes))

def tree_get(tree, index, size):
  (tag, left, right) = tree
  if size == 1:
    return left
  else:
    half = size / 2
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def tree_set(tree, index, size, value):
  (tag, left, right) = tree
  if size == 1:
    return (0, value, 0)
  else:
    half = size / 2
    if index < half:
      new_left = tree_set(left, index, half, value)
      return (1, new_left, right)
    else:
      new_right = tree_set(right, index - half, half, value)
      return (1, left, new_right)

def find_root(node, parents, capacity):
  parent = tree_get(parents, node, capacity)
  if parent == node:
    return node
  else:
    return find_root(parent, parents, capacity)

def merge_edges(edges, parents, sizes, capacity):
  match edges:
    case List/Nil:
      return (parents, sizes)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(u, parents, capacity)
      root_v = find_root(v, parents, capacity)
      if root_u == root_v:
        return merge_edges(edges.tail, parents, sizes, capacity)
      else:
        size_u = tree_get(sizes, root_u, capacity)
        size_v = tree_get(sizes, root_v, capacity)
        if size_u < size_v:
          new_parents = tree_set(parents, root_u, capacity, root_v)
          new_sizes = tree_set(sizes, root_v, capacity, size_u + size_v)
          return merge_edges(edges.tail, new_parents, new_sizes, capacity)
        else:
          new_parents = tree_set(parents, root_v, capacity, root_u)
          new_sizes = tree_set(sizes, root_u, capacity, size_u + size_v)
          return merge_edges(edges.tail, new_parents, new_sizes, capacity)

def answer_queries(queries, parents, capacity):
  match queries:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (a, b) = queries.head
      if a == b:
        return List/Cons(1, answer_queries(queries.tail, parents, capacity))
      else:
        root_a = find_root(a, parents, capacity)
        root_b = find_root(b, parents, capacity)
        if root_a == root_b:
          return List/Cons(1, answer_queries(queries.tail, parents, capacity))
        else:
          return List/Cons(0, answer_queries(queries.tail, parents, capacity))
