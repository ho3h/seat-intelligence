type Tree: Leaf { value } | Branch { left, right }

def prog(x):
  (n, edges) = x
  size = capacity(n, 1)
  adj = empty_tree(size)
  adj2 = build_adj(edges, adj, size)
  meta = meta_tree(size)
  return count_roots(0, n, adj2, size, meta, 0, 0)

def capacity(n, size):
  if size >= n:
    return size
  else:
    return capacity(n, size * 2)

def empty_tree(size):
  if size == 1:
    return Tree/Leaf([])
  else:
    half = size / 2
    return Tree/Branch(empty_tree(half), empty_tree(half))

def meta_tree(size):
  if size == 1:
    return Tree/Leaf((0, 0))
  else:
    half = size / 2
    return Tree/Branch(meta_tree(half), meta_tree(half))

def tree_get(tree, i, size):
  match tree:
    case Tree/Leaf:
      return tree.value
    case Tree/Branch:
      half = size / 2
      if i < half:
        return tree_get(tree.left, i, half)
      else:
        return tree_get(tree.right, i - half, half)

def tree_set(tree, i, size, value):
  match tree:
    case Tree/Leaf:
      return Tree/Leaf(value)
    case Tree/Branch:
      half = size / 2
      if i < half:
        return Tree/Branch(tree_set(tree.left, i, half, value), tree.right)
      else:
        return Tree/Branch(tree.left, tree_set(tree.right, i - half, half, value))

def add_neighbor(adj, vertex, neighbor, size):
  ns = tree_get(adj, vertex, size)
  return tree_set(adj, vertex, size, List/Cons(neighbor, ns))

def build_adj(edges, adj, size):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_neighbor(adj, u, v, size)
      adj2 = add_neighbor(adj1, v, u, size)
      return build_adj(edges.tail, adj2, size)

def dfs(u, parent, adj, size, meta, timer, bridges):
  time = timer + 1
  meta1 = tree_set(meta, u, size, (time, time))
  ns = tree_get(adj, u, size)
  return scan_neighbors(u, parent, ns, adj, size, meta1, time, bridges, time, time)

def scan_neighbors(u, parent, ns, adj, size, meta, timer, bridges, disc_u, low_u):
  match ns:
    case List/Nil:
      return (meta, timer, bridges)
    case List/Cons:
      v = ns.head
      (disc_v, low_v) = tree_get(meta, v, size)
      if disc_v == 0:
        child_disc = timer + 1
        (meta2, timer2, bridges2) = dfs(v, u, adj, size, meta, timer, bridges)
        (ignored_disc, low_child) = tree_get(meta2, v, size)
        if low_child > disc_u:
          bridges3 = bridges2 + 1
        else:
          bridges3 = bridges2
        if low_child < low_u:
          low_u2 = low_child
          meta3 = tree_set(meta2, u, size, (disc_u, low_u2))
        else:
          low_u2 = low_u
          meta3 = meta2
        return scan_neighbors(u, parent, ns.tail, adj, size, meta3, timer2, bridges3, disc_u, low_u2)
      else:
        if v != parent:
          if disc_v < low_u:
            meta2 = tree_set(meta, u, size, (disc_u, disc_v))
            low_u2 = disc_v
          else:
            meta2 = meta
            low_u2 = low_u
          return scan_neighbors(u, parent, ns.tail, adj, size, meta2, timer, bridges, disc_u, low_u2)
        else:
          return scan_neighbors(u, parent, ns.tail, adj, size, meta, timer, bridges, disc_u, low_u)

def count_roots(i, n, adj, size, meta, timer, bridges):
  if i == n:
    return bridges
  else:
    (disc_i, low_i) = tree_get(meta, i, size)
    if disc_i == 0:
      (meta2, timer2, bridges2) = dfs(i, n, adj, size, meta, timer, bridges)
      return count_roots(i + 1, n, adj, size, meta2, timer2, bridges2)
    else:
      return count_roots(i + 1, n, adj, size, meta, timer, bridges)
