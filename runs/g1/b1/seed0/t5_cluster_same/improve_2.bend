def prog(x):
  (n, pairs, queries) = x
  capacity = tree_capacity(n, 1)
  tree = build_tree(capacity, 0, n)
  final_tree = merge_edges(pairs, tree, capacity)
  return answer_queries(queries, final_tree, capacity)

def tree_capacity(n, size):
  if size >= n:
    return size
  else:
    return tree_capacity(n, size * 2)

def build_tree(size, base, n):
  if size == 1:
    if base < n:
      return (0, base, 0)
    else:
      return (0, 0, 0)
  else:
    half = size / 2
    left = build_tree(half, base, n)
    right = build_tree(half, base + half, n)
    return (1, left, right)

def tree_get(tree, index, size):
  (tag, left, right) = tree
  if size == 1:
    return (left, right)
  else:
    half = size / 2
    if index < half:
      return tree_get(left, index, half)
    else:
      return tree_get(right, index - half, half)

def tree_set(tree, index, size, parent, rank):
  (tag, left, right) = tree
  if size == 1:
    return (0, parent, rank)
  else:
    half = size / 2
    if index < half:
      new_left = tree_set(left, index, half, parent, rank)
      return (1, new_left, right)
    else:
      new_right = tree_set(right, index - half, half, parent, rank)
      return (1, left, new_right)

def find_root_info(node, tree, capacity):
  (parent, rank) = tree_get(tree, node, capacity)
  if parent == node:
    return (node, rank)
  else:
    return find_root_info(parent, tree, capacity)

def merge_edges(edges, tree, capacity):
  match edges:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v) = edges.head
      (root_u, rank_u) = find_root_info(u, tree, capacity)
      (root_v, rank_v) = find_root_info(v, tree, capacity)
      if root_u == root_v:
        return merge_edges(edges.tail, tree, capacity)
      else:
        if rank_u < rank_v:
          new_tree = tree_set(tree, root_u, capacity, root_v, rank_u)
          return merge_edges(edges.tail, new_tree, capacity)
        else:
          if rank_u > rank_v:
            new_tree = tree_set(tree, root_v, capacity, root_u, rank_v)
            return merge_edges(edges.tail, new_tree, capacity)
          else:
            tree1 = tree_set(tree, root_v, capacity, root_u, rank_v)
            tree2 = tree_set(tree1, root_u, capacity, root_u, rank_u + 1)
            return merge_edges(edges.tail, tree2, capacity)

def answer_queries(queries, tree, capacity):
  match queries:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (a, b) = queries.head
      (root_a, rank_a) = find_root_info(a, tree, capacity)
      (root_b, rank_b) = find_root_info(b, tree, capacity)
      if root_a == root_b:
        return List/Cons(1, answer_queries(queries.tail, tree, capacity))
      else:
        return List/Cons(0, answer_queries(queries.tail, tree, capacity))
