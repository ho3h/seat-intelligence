def prog(x):
  (n, edges) = x
  if n == 0:
    return 0
  else:
    span = capacity(n, 1)
    tree = make_tree(0, span)
    return merge_edges(edges, tree, span, n)

def capacity(n, span):
  if span >= n:
    return span
  else:
    return capacity(n, span * 2)

def make_tree(start, span):
  if span == 1:
    return (start, 1)
  else:
    half = span / 2
    left = make_tree(start, half)
    right = make_tree(start + half, half)
    return (left, right)

def tree_get(tree, index, start, span):
  if span == 1:
    return tree
  else:
    (left, right) = tree
    half = span / 2
    mid = start + half
    if index < mid:
      return tree_get(left, index, start, half)
    else:
      return tree_get(right, index, mid, half)

def tree_put(tree, index, value, start, span):
  if span == 1:
    return value
  else:
    (left, right) = tree
    half = span / 2
    mid = start + half
    if index < mid:
      return (tree_put(left, index, value, start, half), right)
    else:
      return (left, tree_put(right, index, value, mid, half))

def tree_put_two(tree, index1, value1, index2, value2, start, span):
  if span == 1:
    return value1
  else:
    (left, right) = tree
    half = span / 2
    mid = start + half
    if index1 < mid:
      if index2 < mid:
        return (tree_put_two(left, index1, value1, index2, value2, start, half), right)
      else:
        new_left = tree_put(left, index1, value1, start, half)
        new_right = tree_put(right, index2, value2, mid, half)
        return (new_left, new_right)
    else:
      if index2 < mid:
        new_left = tree_put(left, index2, value2, start, half)
        new_right = tree_put(right, index1, value1, mid, half)
        return (new_left, new_right)
      else:
        return (left, tree_put_two(right, index1, value1, index2, value2, mid, half))

def find_root(tree, x, span):
  (parent, size) = tree_get(tree, x, 0, span)
  if parent == x:
    return x
  else:
    return find_root(tree, parent, span)

def merge_edges(edges, tree, span, count):
  match edges:
    case List/Nil:
      return count
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(tree, u, span)
      root_v = find_root(tree, v, span)
      if root_u == root_v:
        return merge_edges(edges.tail, tree, span, count)
      else:
        (_, size_u) = tree_get(tree, root_u, 0, span)
        (_, size_v) = tree_get(tree, root_v, 0, span)
        if size_u >= size_v:
          new_tree = tree_put_two(tree, root_u, (root_u, size_u + size_v), root_v, (root_u, size_v), 0, span)
          return merge_edges(edges.tail, new_tree, span, count - 1)
        else:
          new_tree = tree_put_two(tree, root_u, (root_v, size_u), root_v, (root_v, size_u + size_v), 0, span)
          return merge_edges(edges.tail, new_tree, span, count - 1)
