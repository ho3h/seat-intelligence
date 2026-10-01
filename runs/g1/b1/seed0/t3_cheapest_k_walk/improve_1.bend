def prog(x):
  (n, s, t, k, edges) = x
  if s >= n:
    return 16777215
  else:
    if t >= n:
      return 16777215
    else:
      if k == 0:
        if s == t:
          return 0
        else:
          return 16777215
      else:
        old = init_dist_tree(0, n, s)
        incoming = empty_tree(0, n)
        graph = build_incoming(edges, incoming, n)
        return solve(k, n, t, graph, old)

def empty_tree(lo, hi):
  if hi - lo == 1:
    return []
  else:
    mid = (lo + hi) / 2
    left = empty_tree(lo, mid)
    right = empty_tree(mid, hi)
    return (left, right)

def init_dist_tree(lo, hi, s):
  if hi - lo == 1:
    if lo == s:
      return 0
    else:
      return 16777215
  else:
    mid = (lo + hi) / 2
    left = init_dist_tree(lo, mid, s)
    right = init_dist_tree(mid, hi, s)
    return (left, right)

def tree_get(tree, lo, hi, i):
  if hi - lo == 1:
    return tree
  else:
    (left, right) = tree
    mid = (lo + hi) / 2
    if i < mid:
      return tree_get(left, lo, mid, i)
    else:
      return tree_get(right, mid, hi, i)

def tree_set(tree, lo, hi, i, value):
  if hi - lo == 1:
    return value
  else:
    (left, right) = tree
    mid = (lo + hi) / 2
    if i < mid:
      new_left = tree_set(left, lo, mid, i, value)
      return (new_left, right)
    else:
      new_right = tree_set(right, mid, hi, i, value)
      return (left, new_right)

def build_incoming(edges, incoming, n):
  match edges:
    case List/Nil:
      return incoming
    case List/Cons:
      (u, v, w) = edges.head
      if u >= n:
        return build_incoming(edges.tail, incoming, n)
      else:
        if v >= n:
          return build_incoming(edges.tail, incoming, n)
        else:
          previous = tree_get(incoming, 0, n, v)
          updated = tree_set(incoming, 0, n, v, List/Cons((u, w), previous))
          return build_incoming(edges.tail, updated, n)

def best_incoming(edges, old, n, best):
  match edges:
    case List/Nil:
      return best
    case List/Cons:
      (u, w) = edges.head
      du = tree_get(old, 0, n, u)
      if du == 16777215:
        return best_incoming(edges.tail, old, n, best)
      else:
        room = 16777215 - du
        if w >= room:
          return best_incoming(edges.tail, old, n, best)
        else:
          candidate = du + w
          if candidate < best:
            return best_incoming(edges.tail, old, n, candidate)
          else:
            return best_incoming(edges.tail, old, n, best)

def make_next(old, old_part, incoming_part, lo, hi, n):
  if hi - lo == 1:
    return best_incoming(incoming_part, old, n, 16777215)
  else:
    (old_left, old_right) = old_part
    (in_left, in_right) = incoming_part
    mid = (lo + hi) / 2
    left = make_next(old, old_left, in_left, lo, mid, n)
    right = make_next(old, old_right, in_right, mid, hi, n)
    return (left, right)

def solve(k, n, t, incoming, old):
  if k == 0:
    return tree_get(old, 0, n, t)
  else:
    updated = make_next(old, old, incoming, 0, n, n)
    return solve(k - 1, n, t, incoming, updated)
