type Dsu: Leaf { parent, size } | Branch { left, right }

def prog(x):
  (n, tau, cands) = x
  if n == 0:
    return 0
  else:
    tree = build_tree(0, n)
    return process_edges(cands, tau, tree, n, 0)

def build_tree(lo, hi):
  if hi - lo == 1:
    return Dsu/Leaf(lo, 1)
  else:
    mid = (lo + hi) / 2
    left = build_tree(lo, mid)
    right = build_tree(mid, hi)
    return Dsu/Branch(left, right)

def tree_parent(tree, lo, hi, index):
  match tree:
    case Dsu/Leaf:
      return tree.parent
    case Dsu/Branch:
      mid = (lo + hi) / 2
      if index < mid:
        return tree_parent(tree.left, lo, mid, index)
      else:
        return tree_parent(tree.right, mid, hi, index)

def tree_size(tree, lo, hi, index):
  match tree:
    case Dsu/Leaf:
      return tree.size
    case Dsu/Branch:
      mid = (lo + hi) / 2
      if index < mid:
        return tree_size(tree.left, lo, mid, index)
      else:
        return tree_size(tree.right, mid, hi, index)

def set_parent(tree, lo, hi, index, value):
  match tree:
    case Dsu/Leaf:
      return Dsu/Leaf(value, tree.size)
    case Dsu/Branch:
      mid = (lo + hi) / 2
      if index < mid:
        left = set_parent(tree.left, lo, mid, index, value)
        return Dsu/Branch(left, tree.right)
      else:
        right = set_parent(tree.right, mid, hi, index, value)
        return Dsu/Branch(tree.left, right)

def set_size(tree, lo, hi, index, value):
  match tree:
    case Dsu/Leaf:
      return Dsu/Leaf(tree.parent, value)
    case Dsu/Branch:
      mid = (lo + hi) / 2
      if index < mid:
        left = set_size(tree.left, lo, mid, index, value)
        return Dsu/Branch(left, tree.right)
      else:
        right = set_size(tree.right, mid, hi, index, value)
        return Dsu/Branch(tree.left, right)

def find_root(tree, lo, hi, index):
  parent = tree_parent(tree, lo, hi, index)
  if parent == index:
    return (index, tree)
  else:
    (root, compressed) = find_root(tree, lo, hi, parent)
    updated = set_parent(compressed, lo, hi, index, root)
    return (root, updated)

def process_edges(edges, tau, tree, n, count):
  if count == n - 1:
    return count
  else:
    match edges:
      case List/Nil:
        return count
      case List/Cons:
        (u, v, score) = edges.head
        if score < tau:
          return process_edges(edges.tail, tau, tree, n, count)
        else:
          (root_u, tree1) = find_root(tree, 0, n, u)
          (root_v, tree2) = find_root(tree1, 0, n, v)
          if root_u == root_v:
            return process_edges(edges.tail, tau, tree2, n, count)
          else:
            size_u = tree_size(tree2, 0, n, root_u)
            size_v = tree_size(tree2, 0, n, root_v)
            if size_u < size_v:
              tree3 = set_parent(tree2, 0, n, root_u, root_v)
              tree4 = set_size(tree3, 0, n, root_v, size_u + size_v)
              return process_edges(edges.tail, tau, tree4, n, count + 1)
            else:
              tree3 = set_parent(tree2, 0, n, root_v, root_u)
              tree4 = set_size(tree3, 0, n, root_u, size_u + size_v)
              return process_edges(edges.tail, tau, tree4, n, count + 1)
