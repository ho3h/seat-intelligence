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
        dist0 = make_tree(depth, 16777215)
        dist = tree_set(dist0, depth, s, 0)
        done = make_tree(depth, 0)
        return dijkstra(n, s, t, depth, edges, dist, done)

def tree_depth(n, capacity, depth):
  if capacity >= n:
    return depth
  else:
    return tree_depth(n, capacity * 2, depth + 1)

def make_tree(depth, value):
  switch depth:
    case 0:
      return Tree/Leaf(value)
    case _:
      left = make_tree(depth - 1, value)
      right = make_tree(depth - 1, value)
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

def select_best(k, index, n, depth, dist, done, best_index, best_value):
  switch k:
    case 0:
      return (best_index, best_value)
    case _:
      is_done = tree_get(done, depth, index)
      if is_done == 0:
        value = tree_get(dist, depth, index)
        if value < best_value:
          return select_best(k - 1, index + 1, n, depth, dist, done, index, value)
        else:
          return select_best(k - 1, index + 1, n, depth, dist, done, best_index, best_value)
      else:
        return select_best(k - 1, index + 1, n, depth, dist, done, best_index, best_value)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def try_relax(u, v, w, current, n, depth, dist, done, current_value):
  if u == current:
    if v < n:
      return relax_neighbor(v, w, n, depth, dist, done, current_value)
    else:
      return dist
  else:
    if v == current:
      if u < n:
        return relax_neighbor(u, w, n, depth, dist, done, current_value)
      else:
        return dist
    else:
      return dist

def relax_neighbor(neighbor, weight, n, depth, dist, done, current_value):
  is_done = tree_get(done, depth, neighbor)
  if is_done == 1:
    return dist
  else:
    old_value = tree_get(dist, depth, neighbor)
    candidate = max2(current_value, weight)
    if candidate < old_value:
      return tree_set(dist, depth, neighbor, candidate)
    else:
      return dist

def relax_edges(edges, current, n, depth, dist, done, current_value):
  match edges:
    case List/Nil:
      return dist
    case List/Cons:
      (u, v, w) = edges.head
      dist1 = try_relax(u, v, w, current, n, depth, dist, done, current_value)
      return relax_edges(edges.tail, current, n, depth, dist1, done, current_value)

def dijkstra(n, s, t, depth, edges, dist, done):
  (best_index, best_value) = select_best(n, 0, n, depth, dist, done, n, 16777215)
  if best_index == n:
    return 16777215
  else:
    if best_index == t:
      return best_value
    else:
      done1 = tree_set(done, depth, best_index, 1)
      dist1 = relax_edges(edges, best_index, n, depth, dist, done1, best_value)
      return dijkstra(n, s, t, depth, edges, dist1, done1)
