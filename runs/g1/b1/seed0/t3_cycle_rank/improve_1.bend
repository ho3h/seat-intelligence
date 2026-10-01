type Tree: Leaf { parent, rank } | Node { left, right, left_size }

def prog(x):
  (n, edges) = x
  parents = init_tree(0, n)
  return process_edges(edges, parents, 0)

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

def get_parent(tree, index):
  match tree:
    case Tree/Leaf:
      return tree.parent
    case Tree/Node:
      if index < tree.left_size:
        return get_parent(tree.left, index)
      else:
        return get_parent(tree.right, index - tree.left_size)

def get_rank(tree, index):
  match tree:
    case Tree/Leaf:
      return tree.rank
    case Tree/Node:
      if index < tree.left_size:
        return get_rank(tree.left, index)
      else:
        return get_rank(tree.right, index - tree.left_size)

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

def find_root(tree, index):
  parent = get_parent(tree, index)
  if parent == index:
    return (index, tree)
  else:
    (root, updated_tree) = find_root(tree, parent)
    compressed_tree = set_parent(updated_tree, index, root)
    return (root, compressed_tree)

def process_edges(edges, parents, cycles):
  match edges:
    case List/Nil:
      return cycles
    case List/Cons:
      (u, v) = edges.head
      (root_u, parents1) = find_root(parents, u)
      (root_v, parents2) = find_root(parents1, v)
      if root_u == root_v:
        return process_edges(edges.tail, parents2, cycles + 1)
      else:
        rank_u = get_rank(parents2, root_u)
        rank_v = get_rank(parents2, root_v)
        if rank_u < rank_v:
          merged = set_parent(parents2, root_u, root_v)
          return process_edges(edges.tail, merged, cycles)
        else:
          if rank_u > rank_v:
            merged = set_parent(parents2, root_v, root_u)
            return process_edges(edges.tail, merged, cycles)
          else:
            linked = set_parent(parents2, root_v, root_u)
            raised = increment_rank(linked, root_u)
            return process_edges(edges.tail, raised, cycles)
