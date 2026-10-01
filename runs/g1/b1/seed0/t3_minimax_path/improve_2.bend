type Tree: Leaf { value } | Node { left, right }

def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return 16777215
  else:
    if t >= n:
      return 16777215
    else:
      if s == t:
        return 0
      else:
        depth = tree_depth(n, 1, 0)
        reachable = is_connected(n, s, t, edges, 16777215, depth)
        if reachable == 0:
          return 16777215
        else:
          return search_threshold(0, 16777215, n, s, t, edges, depth)

def tree_depth(n, capacity, depth):
  if capacity >= n:
    return depth
  else:
    return tree_depth(n, capacity * 2, depth + 1)

def make_parent_tree(depth, start):
  switch depth:
    case 0:
      return Tree/Leaf(start)
    case _:
      half = 1 << (depth - 1)
      left = make_parent_tree(depth - 1, start)
      right = make_parent_tree(depth - 1, start + half)
      return Tree/Node(left, right)

def make_size_tree(depth):
  switch depth:
    case 0:
      return Tree/Leaf(1)
    case _:
      left = make_size_tree(depth - 1)
      right = make_size_tree(depth - 1)
      return Tree/Node(left, right)

def tree_get(tree, depth, index):
  switch depth:
    case 0:
      match tree:
        case Tree/Leaf:
          return tree.value
        case Tree/Node:
          return tree_get(tree.left, 0, index)
    case _:
      match tree:
        case Tree/Leaf:
          return tree.value
        case Tree/Node:
          half = 1 << (depth - 1)
          if index < half:
            return tree_get(tree.left, depth - 1, index)
          else:
            return tree_get(tree.right, depth - 1, index - half)

def tree_set(tree, depth, index, value):
  switch depth:
    case 0:
      match tree:
        case Tree/Leaf:
          return Tree/Leaf(value)
        case Tree/Node:
          return tree
    case _:
      match tree:
        case Tree/Leaf:
          return tree
        case Tree/Node:
          half = 1 << (depth - 1)
          if index < half:
            left = tree_set(tree.left, depth - 1, index, value)
            return Tree/Node(left, tree.right)
          else:
            right = tree_set(tree.right, depth - 1, index - half, value)
            return Tree/Node(tree.left, right)

def find_root(parent, depth, vertex):
  root = tree_get(parent, depth, vertex)
  if root == vertex:
    return vertex
  else:
    return find_root(parent, depth, root)

def union_edges(edges, limit, n, depth, parent, sizes):
  match edges:
    case List/Nil:
      return (parent, sizes)
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          if w <= limit:
            ru = find_root(parent, depth, u)
            rv = find_root(parent, depth, v)
            if ru == rv:
              return union_edges(edges.tail, limit, n, depth, parent, sizes)
            else:
              size_u = tree_get(sizes, depth, ru)
              size_v = tree_get(sizes, depth, rv)
              if size_u < size_v:
                parent1 = tree_set(parent, depth, ru, rv)
                sizes1 = tree_set(sizes, depth, rv, size_u + size_v)
                return union_edges(edges.tail, limit, n, depth, parent1, sizes1)
              else:
                parent1 = tree_set(parent, depth, rv, ru)
                sizes1 = tree_set(sizes, depth, ru, size_u + size_v)
                return union_edges(edges.tail, limit, n, depth, parent1, sizes1)
          else:
            return union_edges(edges.tail, limit, n, depth, parent, sizes)
        else:
          return union_edges(edges.tail, limit, n, depth, parent, sizes)
      else:
        return union_edges(edges.tail, limit, n, depth, parent, sizes)

def is_connected(n, s, t, edges, limit, depth):
  parent = make_parent_tree(depth, 0)
  sizes = make_size_tree(depth)
  (parent1, sizes1) = union_edges(edges, limit, n, depth, parent, sizes)
  root_s = find_root(parent1, depth, s)
  root_t = find_root(parent1, depth, t)
  if root_s == root_t:
    return 1
  else:
    return 0

def search_threshold(low, high, n, s, t, edges, depth):
  if low >= high:
    return low
  else:
    middle = low + (high - low) / 2
    connected = is_connected(n, s, t, edges, middle, depth)
    if connected == 1:
      return search_threshold(low, middle, n, s, t, edges, depth)
    else:
      return search_threshold(middle + 1, high, n, s, t, edges, depth)
