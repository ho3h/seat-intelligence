type Adj: Empty | Leaf {u, w} | Branch {left, right}

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
        entries = init_entries(0, n)
        entries2 = build_incoming(edges, entries, n)
        graph = make_adj_tree(entries2, 0, n, n)
        return solve(k, n, t, graph, old)

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

def init_entries(lo, hi):
  if hi - lo == 1:
    return (0, [])
  else:
    mid = (lo + hi) / 2
    left = init_entries(lo, mid)
    right = init_entries(mid, hi)
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

def build_incoming(edges, entries, n):
  match edges:
    case List/Nil:
      return entries
    case List/Cons:
      (u, v, w) = edges.head
      if u >= n:
        return build_incoming(edges.tail, entries, n)
      else:
        if v >= n:
          return build_incoming(edges.tail, entries, n)
        else:
          (count, incoming) = tree_get(entries, 0, n, v)
          updated = tree_set(entries, 0, n, v, (count + 1, List/Cons((u, w), incoming)))
          return build_incoming(edges.tail, updated, n)

def balanced_adj(xs, count):
  if count == 0:
    return (Adj/Empty, xs)
  else:
    if count == 1:
      match xs:
        case List/Nil:
          return (Adj/Empty, [])
        case List/Cons:
          (u, w) = xs.head
          return (Adj/Leaf(u, w), xs.tail)
    else:
      left_count = count / 2
      right_count = count - left_count
      (left, rest) = balanced_adj(xs, left_count)
      (right, rest2) = balanced_adj(rest, right_count)
      return (Adj/Branch(left, right), rest2)

def make_adj_tree(entries, lo, hi, n):
  if hi - lo == 1:
    (count, incoming) = entries
    (adj, rest) = balanced_adj(incoming, count)
    return adj
  else:
    (entries_left, entries_right) = entries
    mid = (lo + hi) / 2
    left = make_adj_tree(entries_left, lo, mid, n)
    right = make_adj_tree(entries_right, mid, hi, n)
    return (left, right)

def min2(a, b):
  if a < b:
    return a
  else:
    return b

def best_adj(adj, old, n):
  match adj:
    case Adj/Empty:
      return 16777215
    case Adj/Leaf:
      du = tree_get(old, 0, n, adj.u)
      if du == 16777215:
        return 16777215
      else:
        room = 16777215 - du
        if adj.w >= room:
          return 16777215
        else:
          return du + adj.w
    case Adj/Branch:
      left_best = best_adj(adj.left, old, n)
      right_best = best_adj(adj.right, old, n)
      return min2(left_best, right_best)

def make_next(old, old_part, incoming_part, lo, hi, n):
  if hi - lo == 1:
    return best_adj(incoming_part, old, n)
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
