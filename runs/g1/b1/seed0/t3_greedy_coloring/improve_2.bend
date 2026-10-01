def prog(x):
  (n, edges) = x
  height = tree_height(n, 0, 1)
  adjacency = build_tree(height, [])
  adjacency = add_edges(edges, adjacency, height)
  colors = build_tree(height, 0)
  colors_rev = color_vertices(0, n, adjacency, colors, height, [])
  return reverse_list(colors_rev, [])

def tree_height(n, height, capacity):
  if capacity >= n:
    return height
  else:
    return tree_height(n, height + 1, capacity * 2)

def build_tree(height, value):
  if height == 0:
    return value
  else:
    child = build_tree(height - 1, value)
    return (child, child)

def tree_get(tree, index, height):
  if height == 0:
    return tree
  else:
    (left, right) = tree
    half = 1 << (height - 1)
    if index < half:
      return tree_get(left, index, height - 1)
    else:
      return tree_get(right, index - half, height - 1)

def tree_set(tree, index, value, height):
  if height == 0:
    return value
  else:
    (left, right) = tree
    half = 1 << (height - 1)
    if index < half:
      new_left = tree_set(left, index, value, height - 1)
      return (new_left, right)
    else:
      new_right = tree_set(right, index - half, value, height - 1)
      return (left, new_right)

def add_edges(edges, adjacency, height):
  match edges:
    case List/Nil:
      return adjacency
    case List/Cons:
      (a, b) = edges.head
      neighbors_a = tree_get(adjacency, a, height)
      adjacency = tree_set(adjacency, a, List/Cons(b, neighbors_a), height)
      neighbors_b = tree_get(adjacency, b, height)
      adjacency = tree_set(adjacency, b, List/Cons(a, neighbors_b), height)
      return add_edges(edges.tail, adjacency, height)

def color_vertices(v, n, adjacency, colors, height, colors_rev):
  if v == n:
    return colors_rev
  else:
    neighbors = tree_get(adjacency, v, height)
    used = collect_used(v, neighbors, colors, height, [])
    color = find_available(used, 0)
    colors = tree_set(colors, v, color, height)
    return color_vertices(v + 1, n, adjacency, colors, height, List/Cons(color, colors_rev))

def collect_used(v, neighbors, colors, height, used):
  match neighbors:
    case List/Nil:
      return used
    case List/Cons:
      neighbor = neighbors.head
      if neighbor < v:
        color = tree_get(colors, neighbor, height)
        return collect_used(v, neighbors.tail, colors, height, List/Cons(color, used))
      else:
        return collect_used(v, neighbors.tail, colors, height, used)

def find_available(used, color):
  if contains_color(used, color):
    return find_available(used, color + 1)
  else:
    return color

def contains_color(xs, color):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == color:
        return 1
      else:
        return contains_color(xs.tail, color)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))
