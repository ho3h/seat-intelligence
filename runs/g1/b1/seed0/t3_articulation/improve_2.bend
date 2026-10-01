type Tree: Leaf { value } | Node { left, right }

def prog(x):
  (n, edges) = x
  (size, depth) = choose_depth(n, 1, 0)
  adj0 = make_tree(depth, [])
  adj = build_adj(edges, adj0, depth)
  zeros = make_tree(depth, 0)
  (clock, disc, low, arts) = visit_all(0, n, adj, n, depth, 0, zeros, zeros, zeros)
  return count_tree(arts)

def choose_depth(n, size, depth):
  if size >= n:
    return (size, depth)
  else:
    return choose_depth(n, size * 2, depth + 1)

def make_tree(depth, initial):
  switch depth:
    case 0:
      return Tree/Leaf(initial)
    case _:
      left = make_tree(depth - 1, initial)
      right = make_tree(depth - 1, initial)
      return Tree/Node(left, right)

def get_tree(tree, index, depth):
  match tree:
    case Tree/Leaf:
      return tree.value
    case Tree/Node:
      half = 1 << (depth - 1)
      if index < half:
        return get_tree(tree.left, index, depth - 1)
      else:
        return get_tree(tree.right, index - half, depth - 1)

def set_tree(tree, index, value, depth):
  match tree:
    case Tree/Leaf:
      return Tree/Leaf(value)
    case Tree/Node:
      half = 1 << (depth - 1)
      if index < half:
        left = set_tree(tree.left, index, value, depth - 1)
        return Tree/Node(left, tree.right)
      else:
        right = set_tree(tree.right, index - half, value, depth - 1)
        return Tree/Node(tree.left, right)

def build_adj(edges, adj, depth):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_neighbor(adj, u, v, depth)
      adj2 = add_neighbor(adj1, v, u, depth)
      return build_adj(edges.tail, adj2, depth)

def add_neighbor(adj, index, neighbor, depth):
  neighbors = get_tree(adj, index, depth)
  updated = List/Cons(neighbor, neighbors)
  return set_tree(adj, index, updated, depth)

def visit_all(i, n, adj, sentinel, depth, clock, disc, low, arts):
  if i == n:
    return (clock, disc, low, arts)
  else:
    if get_tree(disc, i, depth) != 0:
      return visit_all(i + 1, n, adj, sentinel, depth, clock, disc, low, arts)
    else:
      (clock2, disc2, low2, arts2) = visit_vertex(i, sentinel, sentinel, adj, depth, clock, disc, low, arts)
      return visit_all(i + 1, n, adj, sentinel, depth, clock2, disc2, low2, arts2)

def visit_vertex(u, parent, sentinel, adj, depth, clock, disc, low, arts):
  clock2 = clock + 1
  disc2 = set_tree(disc, u, clock2, depth)
  low2 = set_tree(low, u, clock2, depth)
  neighbors = get_tree(adj, u, depth)
  return visit_neighbors(neighbors, u, parent, sentinel, adj, depth, clock2, disc2, low2, arts, 0)

def visit_neighbors(neighbors, u, parent, sentinel, adj, depth, clock, disc, low, arts, children):
  match neighbors:
    case List/Nil:
      if parent == sentinel:
        if children > 1:
          arts2 = set_tree(arts, u, 1, depth)
          return (clock, disc, low, arts2)
        else:
          return (clock, disc, low, arts)
      else:
        return (clock, disc, low, arts)
    case List/Cons:
      v = neighbors.head
      if v == parent:
        return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, depth, clock, disc, low, arts, children)
      else:
        if get_tree(disc, v, depth) == 0:
          (clock2, disc2, low2, arts2) = visit_vertex(v, u, sentinel, adj, depth, clock, disc, low, arts)
          child_low = get_tree(low2, v, depth)
          u_low = get_tree(low2, u, depth)
          if child_low < u_low:
            low3 = set_tree(low2, u, child_low, depth)
          else:
            low3 = low2
          if parent != sentinel:
            u_disc = get_tree(disc2, u, depth)
            if child_low >= u_disc:
              arts3 = set_tree(arts2, u, 1, depth)
            else:
              arts3 = arts2
          else:
            arts3 = arts2
          return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, depth, clock2, disc2, low3, arts3, children + 1)
        else:
          neighbor_disc = get_tree(disc, v, depth)
          u_low = get_tree(low, u, depth)
          if neighbor_disc < u_low:
            low2 = set_tree(low, u, neighbor_disc, depth)
          else:
            low2 = low
          return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, depth, clock, disc, low2, arts, children)

def count_tree(tree):
  match tree:
    case Tree/Leaf:
      return tree.value
    case Tree/Node:
      left_count = count_tree(tree.left)
      right_count = count_tree(tree.right)
      return left_count + right_count
