def prog(x):
  (n, edges) = x
  if n == 0:
    return []
  else:
    tree = build_tree(0, n)
    tree2 = union_edges(edges, tree, n)
    return all_labels(tree2, 0, n)

def build_tree(start, size):
  if size == 1:
    return (start, 1, start)
  else:
    left_size = size / 2
    right_size = size - left_size
    left = build_tree(start, left_size)
    right = build_tree(start + left_size, right_size)
    return (left, right)

def tree_get(tree, size, index):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    left_size = size / 2
    right_size = size - left_size
    if index < left_size:
      return tree_get(left, left_size, index)
    else:
      return tree_get(right, right_size, index - left_size)

def tree_set(tree, size, index, value):
  if size == 1:
    return value
  else:
    (left, right) = tree
    left_size = size / 2
    right_size = size - left_size
    if index < left_size:
      new_left = tree_set(left, left_size, index, value)
      return (new_left, right)
    else:
      new_right = tree_set(right, right_size, index - left_size, value)
      return (left, new_right)

def find_root(tree, n, vertex):
  (parent, size, smallest) = tree_get(tree, n, vertex)
  if parent == vertex:
    return vertex
  else:
    return find_root(tree, n, parent)

def min_u(a, b):
  if a < b:
    return a
  else:
    return b

def union_edges(edges, tree, n):
  match edges:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(tree, n, u)
      root_v = find_root(tree, n, v)
      if root_u == root_v:
        return union_edges(edges.tail, tree, n)
      else:
        (parent_u, size_u, min_u_value) = tree_get(tree, n, root_u)
        (parent_v, size_v, min_v_value) = tree_get(tree, n, root_v)
        if size_u < size_v:
          child_record = (root_v, size_u, min_u_value)
          tree1 = tree_set(tree, n, root_u, child_record)
          root_record = (root_v, size_u + size_v, min_u(min_u_value, min_v_value))
          tree2 = tree_set(tree1, n, root_v, root_record)
          return union_edges(edges.tail, tree2, n)
        else:
          child_record = (root_u, size_v, min_v_value)
          tree1 = tree_set(tree, n, root_v, child_record)
          root_record = (root_u, size_u + size_v, min_u(min_u_value, min_v_value))
          tree2 = tree_set(tree1, n, root_u, root_record)
          return union_edges(edges.tail, tree2, n)

def all_labels(tree, vertex, n):
  if vertex == n:
    return []
  else:
    root = find_root(tree, n, vertex)
    (parent, size, smallest) = tree_get(tree, n, root)
    rest = all_labels(tree, vertex + 1, n)
    return List/Cons(smallest, rest)
