type Tree: Leaf { parent, rank } | Node { left, right, left_size }

def prog(x):
  (n, edges) = x
  m = count_list(edges)
  forest = forest_reduce(edges, m, n)
  forest_size = count_list(forest)
  return m - forest_size

def count_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_list(xs.tail)

def forest_reduce(edges, size, n):
  if size <= 2048:
    tree = init_tree(0, n)
    return select_forest(edges, tree, [])
  else:
    left_size = size / 2
    (left_edges, right_edges) = split_at(edges, left_size)
    right_size = size - left_size
    left_forest = forest_reduce(left_edges, left_size, n)
    right_forest = forest_reduce(right_edges, right_size, n)
    combined_edges = concat(left_forest, right_forest)
    tree = init_tree(0, n)
    return select_forest(combined_edges, tree, [])

def split_at(xs, count):
  if count == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (prefix, suffix) = split_at(xs.tail, count - 1)
        return (List/Cons(xs.head, prefix), suffix)

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      rest = concat(xs.tail, ys)
      return List/Cons(xs.head, rest)

def init_tree(start, size):
  if size == 0:
    return Tree/Leaf(0, 0)
  else:
    if size == 1:
      return Tree/Leaf(start, 0)
    else:
      left_size = size / 2
      right_size = size - left_size
      left = init_tree(start, left_size)
      right = init_tree(start + left_size, right_size)
      return Tree/Node(left, right, left_size)

def get_parent_rank(tree, index):
  match tree:
    case Tree/Leaf:
      return (tree.parent, tree.rank)
    case Tree/Node:
      if index < tree.left_size:
        return get_parent_rank(tree.left, index)
      else:
        return get_parent_rank(tree.right, index - tree.left_size)

def find_root(tree, index):
  (parent, rank) = get_parent_rank(tree, index)
  if parent == index:
    return index
  else:
    return find_root(tree, parent)

def set_parent(tree, index, new_parent):
  match tree:
    case Tree/Leaf:
      return Tree/Leaf(new_parent, tree.rank)
    case Tree/Node:
      if index < tree.left_size:
        left = set_parent(tree.left, index, new_parent)
        return Tree/Node(left, tree.right, tree.left_size)
      else:
        right = set_parent(tree.right, index - tree.left_size, new_parent)
        return Tree/Node(tree.left, right, tree.left_size)

def increment_rank(tree, index):
  match tree:
    case Tree/Leaf:
      return Tree/Leaf(tree.parent, tree.rank + 1)
    case Tree/Node:
      if index < tree.left_size:
        left = increment_rank(tree.left, index)
        return Tree/Node(left, tree.right, tree.left_size)
      else:
        right = increment_rank(tree.right, index - tree.left_size)
        return Tree/Node(tree.left, right, tree.left_size)

def link_roots(tree, root_u, root_v):
  (parent_u, rank_u) = get_parent_rank(tree, root_u)
  (parent_v, rank_v) = get_parent_rank(tree, root_v)
  if rank_u < rank_v:
    return set_parent(tree, root_u, root_v)
  else:
    if rank_u > rank_v:
      return set_parent(tree, root_v, root_u)
    else:
      linked = set_parent(tree, root_v, root_u)
      return increment_rank(linked, root_u)

def select_forest(edges, tree, acc):
  match edges:
    case List/Nil:
      return reverse_list(acc)
    case List/Cons:
      (u, v) = edges.head
      root_u = find_root(tree, u)
      root_v = find_root(tree, v)
      if root_u == root_v:
        return select_forest(edges.tail, tree, acc)
      else:
        linked = link_roots(tree, root_u, root_v)
        return select_forest(edges.tail, linked, List/Cons(edges.head, acc))

def reverse_list(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
