def prog(x):
  (n, edges) = x
  size = capacity(n, 1)
  tree = build_tree(size)
  tree = load_edges(edges, tree, size)
  (tree, bad) = process_roots(0, n, size, tree, 0)
  if bad == 1:
    return make_fill(n, 16777215)
  else:
    (remaining, colors) = collect_rev(tree, size, n, [])
    return reverse(colors)

def capacity(n, size):
  if size >= n:
    return size
  else:
    return capacity(n, size * 2)

def build_tree(size):
  if size == 1:
    return ([], 2)
  else:
    half = size / 2
    return (build_tree(half), build_tree(half))

def tree_get(tree, size, index):
  if size == 1:
    return tree
  else:
    half = size / 2
    (left, right) = tree
    if index < half:
      return tree_get(left, half, index)
    else:
      return tree_get(right, half, index - half)

def tree_set(tree, size, index, value):
  if size == 1:
    return value
  else:
    half = size / 2
    (left, right) = tree
    if index < half:
      left = tree_set(left, half, index, value)
      return (left, right)
    else:
      right = tree_set(right, half, index - half, value)
      return (left, right)

def load_edges(edges, tree, size):
  match edges:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v) = edges.head
      (u_adj, u_color) = tree_get(tree, size, u)
      tree = tree_set(tree, size, u, (List/Cons(v, u_adj), u_color))
      (v_adj, v_color) = tree_get(tree, size, v)
      tree = tree_set(tree, size, v, (List/Cons(u, v_adj), v_color))
      return load_edges(edges.tail, tree, size)

def process_roots(i, n, size, tree, bad):
  if bad == 1:
    return (tree, bad)
  else:
    if i == n:
      return (tree, bad)
    else:
      (adj, color) = tree_get(tree, size, i)
      if color == 2:
        tree = tree_set(tree, size, i, (adj, 0))
        (tree, bad) = breadth_first(size, tree, [i], [], 0)
        return process_roots(i + 1, n, size, tree, bad)
      else:
        return process_roots(i + 1, n, size, tree, bad)

def breadth_first(size, tree, front, back, bad):
  if bad == 1:
    return (tree, bad)
  else:
    match front:
      case List/Nil:
        match back:
          case List/Nil:
            return (tree, bad)
          case List/Cons:
            return breadth_first(size, tree, reverse(back), [], bad)
      case List/Cons:
        current = front.head
        (adj, color) = tree_get(tree, size, current)
        (tree, back, bad) = scan_neighbors(adj, color, size, tree, back, 0)
        return breadth_first(size, tree, front.tail, back, bad)

def scan_neighbors(neighbors, color, size, tree, back, bad):
  if bad == 1:
    return (tree, back, bad)
  else:
    match neighbors:
      case List/Nil:
        return (tree, back, bad)
      case List/Cons:
        neighbor = neighbors.head
        expected = 1 - color
        (adj, neighbor_color) = tree_get(tree, size, neighbor)
        if neighbor_color == 2:
          tree = tree_set(tree, size, neighbor, (adj, expected))
          back = List/Cons(neighbor, back)
          return scan_neighbors(neighbors.tail, color, size, tree, back, bad)
        else:
          if neighbor_color != expected:
            return (tree, back, 1)
          else:
            return scan_neighbors(neighbors.tail, color, size, tree, back, bad)

def collect_rev(tree, size, remaining, acc):
  if remaining == 0:
    return (remaining, acc)
  else:
    if size == 1:
      (adj, color) = tree
      return (remaining - 1, List/Cons(color, acc))
    else:
      half = size / 2
      (left, right) = tree
      (remaining, acc) = collect_rev(left, half, remaining, acc)
      return collect_rev(right, half, remaining, acc)

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def make_fill(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_fill(n - 1, value))
