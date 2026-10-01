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
    return capacity(n, span * 4)

def make_tree(start, span):
  if span == 1:
    return (start, 1)
  else:
    quarter = span / 4
    a = make_tree(start, quarter)
    b = make_tree(start + quarter, quarter)
    c = make_tree(start + quarter * 2, quarter)
    d = make_tree(start + quarter * 3, quarter)
    return (a, b, c, d)

def tree_get(tree, index, start, span):
  if span == 1:
    return tree
  else:
    (a, b, c, d) = tree
    quarter = span / 4
    offset = index - start
    if offset < quarter:
      return tree_get(a, index, start, quarter)
    else:
      if offset < quarter * 2:
        return tree_get(b, index, start + quarter, quarter)
      else:
        if offset < quarter * 3:
          return tree_get(c, index, start + quarter * 2, quarter)
        else:
          return tree_get(d, index, start + quarter * 3, quarter)

def tree_put(tree, index, value, start, span):
  if span == 1:
    return value
  else:
    (a, b, c, d) = tree
    quarter = span / 4
    offset = index - start
    if offset < quarter:
      return (tree_put(a, index, value, start, quarter), b, c, d)
    else:
      if offset < quarter * 2:
        return (a, tree_put(b, index, value, start + quarter, quarter), c, d)
      else:
        if offset < quarter * 3:
          return (a, b, tree_put(c, index, value, start + quarter * 2, quarter), d)
        else:
          return (a, b, c, tree_put(d, index, value, start + quarter * 3, quarter))

def tree_put_two(tree, index1, value1, index2, value2, start, span):
  if span == 1:
    return value1
  else:
    (a, b, c, d) = tree
    quarter = span / 4
    q1 = (index1 - start) / quarter
    q2 = (index2 - start) / quarter
    if q1 == q2:
      if q1 == 0:
        return (tree_put_two(a, index1, value1, index2, value2, start, quarter), b, c, d)
      else:
        if q1 == 1:
          return (a, tree_put_two(b, index1, value1, index2, value2, start + quarter, quarter), c, d)
        else:
          if q1 == 2:
            return (a, b, tree_put_two(c, index1, value1, index2, value2, start + quarter * 2, quarter), d)
          else:
            return (a, b, c, tree_put_two(d, index1, value1, index2, value2, start + quarter * 3, quarter))
    else:
      first = tree_put(tree, index1, value1, start, span)
      return tree_put(first, index2, value2, start, span)

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
