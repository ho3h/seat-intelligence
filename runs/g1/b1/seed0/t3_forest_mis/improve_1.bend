def prog(x):
  (n, edges) = x
  if n == 0:
    return 0
  else:
    adjacency = build_adj(0, n)
    adjacency = add_edges(edges, adjacency, n)
    seen = build_seen(0, n)
    return visit_roots(0, n, adjacency, seen, 0)

def build_adj(lo, hi):
  if hi - lo == 1:
    return []
  else:
    mid = (lo + hi) / 2
    left = build_adj(lo, mid)
    right = build_adj(mid, hi)
    return (left, right)

def build_seen(lo, hi):
  if hi - lo == 1:
    return 0
  else:
    mid = (lo + hi) / 2
    left = build_seen(lo, mid)
    right = build_seen(mid, hi)
    return (left, right)

def get_adj(tree, key, lo, hi):
  if hi - lo == 1:
    return tree
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if key < mid:
      return get_adj(left, key, lo, mid)
    else:
      return get_adj(right, key, mid, hi)

def set_adj(tree, key, lo, hi, value):
  if hi - lo == 1:
    return value
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if key < mid:
      next_left = set_adj(left, key, lo, mid, value)
      return (next_left, right)
    else:
      next_right = set_adj(right, key, mid, hi, value)
      return (left, next_right)

def get_seen(tree, key, lo, hi):
  if hi - lo == 1:
    return tree
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if key < mid:
      return get_seen(left, key, lo, mid)
    else:
      return get_seen(right, key, mid, hi)

def set_seen(tree, key, lo, hi, value):
  if hi - lo == 1:
    return value
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if key < mid:
      next_left = set_seen(left, key, lo, mid, value)
      return (next_left, right)
    else:
      next_right = set_seen(right, key, mid, hi, value)
      return (left, next_right)

def add_edges(edges, adjacency, n):
  match edges:
    case List/Nil:
      return adjacency
    case List/Cons:
      (u, v) = edges.head
      u_neighbors = get_adj(adjacency, u, 0, n)
      adjacency1 = set_adj(adjacency, u, 0, n, List/Cons(v, u_neighbors))
      v_neighbors = get_adj(adjacency1, v, 0, n)
      adjacency2 = set_adj(adjacency1, v, 0, n, List/Cons(u, v_neighbors))
      return add_edges(edges.tail, adjacency2, n)

def bigger(a, b):
  if a > b:
    return a
  else:
    return b

def tree_dp(node, parent, has_parent, adjacency, seen, n):
  marked = set_seen(seen, node, 0, n, 1)
  neighbors = get_adj(adjacency, node, 0, n)
  return combine_children(neighbors, node, parent, has_parent, adjacency, marked, n, 1, 0)

def combine_children(children, node, parent, has_parent, adjacency, seen, n, take, leave):
  match children:
    case List/Nil:
      return (take, leave, seen)
    case List/Cons:
      if has_parent == 1:
        if children.head == parent:
          return combine_children(children.tail, node, parent, has_parent, adjacency, seen, n, take, leave)
        else:
          (child_take, child_leave, next_seen) = tree_dp(children.head, node, 1, adjacency, seen, n)
          next_take = take + child_leave
          next_leave = leave + bigger(child_take, child_leave)
          return combine_children(children.tail, node, parent, has_parent, adjacency, next_seen, n, next_take, next_leave)
      else:
        (child_take, child_leave, next_seen) = tree_dp(children.head, node, 1, adjacency, seen, n)
        next_take = take + child_leave
        next_leave = leave + bigger(child_take, child_leave)
        return combine_children(children.tail, node, parent, has_parent, adjacency, next_seen, n, next_take, next_leave)

def visit_roots(i, n, adjacency, seen, total):
  if i == n:
    return total
  else:
    if get_seen(seen, i, 0, n) == 1:
      return visit_roots(i + 1, n, adjacency, seen, total)
    else:
      (take, leave, next_seen) = tree_dp(i, 0, 0, adjacency, seen, n)
      next_total = total + bigger(take, leave)
      return visit_roots(i + 1, n, adjacency, next_seen, next_total)
