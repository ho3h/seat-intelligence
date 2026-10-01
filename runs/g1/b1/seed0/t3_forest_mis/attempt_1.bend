def prog(x):
  (n, edges) = x
  return visit_roots(0, n, edges, [], 0)

def bigger(a, b):
  if a > b:
    return a
  else:
    return b

def join(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, join(xs.tail, ys))

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def get_neighbors(node, edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      if u == node:
        return List/Cons(v, get_neighbors(node, edges.tail))
      else:
        if v == node:
          return List/Cons(u, get_neighbors(node, edges.tail))
        else:
          return get_neighbors(node, edges.tail)

def tree_dp(node, parent, has_parent, edges):
  neighbors = get_neighbors(node, edges)
  return combine_children(neighbors, node, parent, has_parent, edges, 1, 0, [node])

def combine_children(children, node, parent, has_parent, edges, take, leave, nodes):
  match children:
    case List/Nil:
      return (take, leave, nodes)
    case List/Cons:
      if has_parent == 1:
        if children.head == parent:
          return combine_children(children.tail, node, parent, has_parent, edges, take, leave, nodes)
        else:
          (child_take, child_leave, child_nodes) = tree_dp(children.head, node, 1, edges)
          next_nodes = join(nodes, child_nodes)
          next_take = take + child_leave
          next_leave = leave + bigger(child_take, child_leave)
          return combine_children(children.tail, node, parent, has_parent, edges, next_take, next_leave, next_nodes)
      else:
        (child_take, child_leave, child_nodes) = tree_dp(children.head, node, 1, edges)
        next_nodes = join(nodes, child_nodes)
        next_take = take + child_leave
        next_leave = leave + bigger(child_take, child_leave)
        return combine_children(children.tail, node, parent, has_parent, edges, next_take, next_leave, next_nodes)

def visit_roots(i, n, edges, seen, total):
  if i == n:
    return total
  else:
    if contains(seen, i) == 1:
      return visit_roots(i + 1, n, edges, seen, total)
    else:
      (take, leave, component) = tree_dp(i, 0, 0, edges)
      next_seen = join(seen, component)
      next_total = total + bigger(take, leave)
      return visit_roots(i + 1, n, edges, next_seen, next_total)
