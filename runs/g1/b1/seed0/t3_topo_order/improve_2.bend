def prog(x):
  (n, edges) = x
  if n == 0:
    return []
  else:
    indegs = make_indeg_tree(0, n, n)
    adjacency = make_adj_tree(0, n)
    (indegs, adjacency) = process_edges(edges, n, indegs, adjacency)
    return topo_order(n, adjacency, indegs)

def make_indeg_tree(lo, hi, n):
  if lo + 1 == hi:
    return (lo, 0, 0)
  else:
    mid = (lo + hi) / 2
    left = make_indeg_tree(lo, mid, n)
    right = make_indeg_tree(mid, hi, n)
    (lm, _, _) = left
    (rm, _, _) = right
    if lm < rm:
      return (lm, left, right)
    else:
      return (rm, left, right)

def make_adj_tree(lo, hi):
  if lo + 1 == hi:
    return (0, [], 0)
  else:
    mid = (lo + hi) / 2
    left = make_adj_tree(lo, mid)
    right = make_adj_tree(mid, hi)
    return (0, left, right)

def process_edges(edges, n, indegs, adjacency):
  match edges:
    case List/Nil:
      return (indegs, adjacency)
    case List/Cons:
      (u, v) = edges.head
      next_indegs = increment_tree(indegs, 0, n, v, n)
      next_adjacency = add_neighbor(adjacency, 0, n, u, v)
      return process_edges(edges.tail, n, next_indegs, next_adjacency)

def increment_tree(tree, lo, hi, idx, n):
  if lo + 1 == hi:
    (_, value, _) = tree
    new_value = value + 1
    if new_value == 0:
      return (lo, new_value, 0)
    else:
      return (n, new_value, 0)
  else:
    (_, left, right) = tree
    mid = (lo + hi) / 2
    if idx < mid:
      new_left = increment_tree(left, lo, mid, idx, n)
      (lm, _, _) = new_left
      (rm, _, _) = right
      if lm < rm:
        return (lm, new_left, right)
      else:
        return (rm, new_left, right)
    else:
      new_right = increment_tree(right, mid, hi, idx, n)
      (lm, _, _) = left
      (rm, _, _) = new_right
      if lm < rm:
        return (lm, left, new_right)
      else:
        return (rm, left, new_right)

def add_neighbor(tree, lo, hi, idx, neighbor):
  if lo + 1 == hi:
    (_, neighbors, _) = tree
    return (0, List/Cons(neighbor, neighbors), 0)
  else:
    (_, left, right) = tree
    mid = (lo + hi) / 2
    if idx < mid:
      new_left = add_neighbor(left, lo, mid, idx, neighbor)
      return (0, new_left, right)
    else:
      new_right = add_neighbor(right, mid, hi, idx, neighbor)
      return (0, left, new_right)

def get_neighbors(tree, lo, hi, idx):
  if lo + 1 == hi:
    (_, neighbors, _) = tree
    return neighbors
  else:
    (_, left, right) = tree
    mid = (lo + hi) / 2
    if idx < mid:
      return get_neighbors(left, lo, mid, idx)
    else:
      return get_neighbors(right, mid, hi, idx)

def set_tree_value(tree, lo, hi, idx, value, n):
  if lo + 1 == hi:
    if value == 0:
      return (lo, value, 0)
    else:
      return (n, value, 0)
  else:
    (_, left, right) = tree
    mid = (lo + hi) / 2
    if idx < mid:
      new_left = set_tree_value(left, lo, mid, idx, value, n)
      (lm, _, _) = new_left
      (rm, _, _) = right
      if lm < rm:
        return (lm, new_left, right)
      else:
        return (rm, new_left, right)
    else:
      new_right = set_tree_value(right, mid, hi, idx, value, n)
      (lm, _, _) = left
      (rm, _, _) = new_right
      if lm < rm:
        return (lm, left, new_right)
      else:
        return (rm, left, new_right)

def decrement_tree(tree, lo, hi, idx, n):
  if lo + 1 == hi:
    (_, value, _) = tree
    new_value = value - 1
    if new_value == 0:
      return (lo, new_value, 0)
    else:
      return (n, new_value, 0)
  else:
    (_, left, right) = tree
    mid = (lo + hi) / 2
    if idx < mid:
      new_left = decrement_tree(left, lo, mid, idx, n)
      (lm, _, _) = new_left
      (rm, _, _) = right
      if lm < rm:
        return (lm, new_left, right)
      else:
        return (rm, new_left, right)
    else:
      new_right = decrement_tree(right, mid, hi, idx, n)
      (lm, _, _) = left
      (rm, _, _) = new_right
      if lm < rm:
        return (lm, left, new_right)
      else:
        return (rm, left, new_right)

def decrement_neighbors(neighbors, indegs, n):
  match neighbors:
    case List/Nil:
      return indegs
    case List/Cons:
      next_indegs = decrement_tree(indegs, 0, n, neighbors.head, n)
      return decrement_neighbors(neighbors.tail, next_indegs, n)

def topo_order(n, adjacency, indegs):
  (vertex, _, _) = indegs
  if vertex == n:
    return []
  else:
    neighbors = get_neighbors(adjacency, 0, n, vertex)
    marked = set_tree_value(indegs, 0, n, vertex, n, n)
    next_indegs = decrement_neighbors(neighbors, marked, n)
    return List/Cons(vertex, topo_order(n, adjacency, next_indegs))
