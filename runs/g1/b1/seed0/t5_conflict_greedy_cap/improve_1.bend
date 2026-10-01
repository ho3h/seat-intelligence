def prog(x):
  (n, cap, mnl, cands) = x
  state = build_state_tree(0, n)
  state1 = mark_links(mnl, state, n)
  ordered = sort_candidates(cands)
  state2 = process_candidates(ordered, cap, state1, n)
  return build_result(0, n, state2)

def make_state(parent, size, maximum, members, adjacency):
  return (parent, (size, (maximum, (members, adjacency))))

def build_state_tree(lo, hi):
  if lo == hi:
    return []
  else:
    if hi - lo == 1:
      return make_state(lo, 1, lo, List/Cons(lo, []), [])
    else:
      mid = (lo + hi) / 2
      left = build_state_tree(lo, mid)
      right = build_state_tree(mid, hi)
      return (left, right)

def tree_get(tree, lo, hi, index):
  if hi - lo == 1:
    return tree
  else:
    (left, right) = tree
    mid = (lo + hi) / 2
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_set(tree, lo, hi, index, value):
  if hi - lo == 1:
    return value
  else:
    (left, right) = tree
    mid = (lo + hi) / 2
    if index < mid:
      new_left = tree_set(left, lo, mid, index, value)
      return (new_left, right)
    else:
      new_right = tree_set(right, mid, hi, index, value)
      return (left, new_right)

def state_parent(state):
  (parent, rest) = state
  return parent

def state_size(state):
  (parent, rest) = state
  (size, rest2) = rest
  return size

def state_maximum(state):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  return maximum

def state_members(state):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, adjacency) = rest3
  return members

def state_adjacency(state):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, adjacency) = rest3
  return adjacency

def state_with_parent(state, new_parent):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, adjacency) = rest3
  return make_state(new_parent, size, maximum, members, adjacency)

def state_with_merge(state, new_size, new_maximum, new_members):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, adjacency) = rest3
  return make_state(parent, new_size, new_maximum, new_members, adjacency)

def get_parent(tree, n, node):
  state = tree_get(tree, 0, n, node)
  return state_parent(state)

def find_root(tree, n, node):
  parent = get_parent(tree, n, node)
  if parent == node:
    return node
  else:
    return find_root(tree, n, parent)

def append_lists(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_lists(a.tail, b))

def mark_links(links, tree, n):
  match links:
    case List/Nil:
      return tree
    case List/Cons:
      (a, b) = links.head
      state_a = tree_get(tree, 0, n, a)
      adjacency_a = state_adjacency(state_a)
      state_a1 = make_state(
        state_parent(state_a),
        state_size(state_a),
        state_maximum(state_a),
        state_members(state_a),
        List/Cons(b, adjacency_a)
      )
      tree1 = tree_set(tree, 0, n, a, state_a1)
      state_b = tree_get(tree1, 0, n, b)
      adjacency_b = state_adjacency(state_b)
      state_b1 = make_state(
        state_parent(state_b),
        state_size(state_b),
        state_maximum(state_b),
        state_members(state_b),
        List/Cons(a, adjacency_b)
      )
      tree2 = tree_set(tree1, 0, n, b, state_b1)
      return mark_links(links.tail, tree2, n)

def neighbor_conflict(neighbors, tree, n, other_root):
  match neighbors:
    case List/Nil:
      return 0
    case List/Cons:
      root = find_root(tree, n, neighbors.head)
      if root == other_root:
        return 1
      else:
        return neighbor_conflict(neighbors.tail, tree, n, other_root)

def cluster_conflict(nodes, tree, n, other_root):
  match nodes:
    case List/Nil:
      return 0
    case List/Cons:
      state = tree_get(tree, 0, n, nodes.head)
      neighbors = state_adjacency(state)
      if neighbor_conflict(neighbors, tree, n, other_root) == 1:
        return 1
      else:
        return cluster_conflict(nodes.tail, tree, n, other_root)

def before(a, b):
  (au, av, ass) = a
  (bu, bv, bss) = b
  if ass > bss:
    return 1
  else:
    if ass < bss:
      return 0
    else:
      if au < bu:
        return 1
      else:
        if au > bu:
          return 0
        else:
          return av < bv

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, []), [])
        case List/Cons:
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_sorted(a.tail, b))
          else:
            return List/Cons(b.head, merge_sorted(a, b.tail))

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return List/Cons(xs.head, [])
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort_candidates(left)
          sorted_right = sort_candidates(right)
          return merge_sorted(sorted_left, sorted_right)

def process_candidates(cands, cap, tree, n):
  match cands:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v, score) = cands.head
      ru = find_root(tree, n, u)
      rv = find_root(tree, n, v)
      if ru == rv:
        return process_candidates(cands.tail, cap, tree, n)
      else:
        state_u = tree_get(tree, 0, n, ru)
        state_v = tree_get(tree, 0, n, rv)
        size_u = state_size(state_u)
        size_v = state_size(state_v)
        total = size_u + size_v
        if total > cap:
          return process_candidates(cands.tail, cap, tree, n)
        else:
          return attempt_merge(cands.tail, cap, tree, n, ru, rv, state_u, state_v, size_u, size_v, total)

def attempt_merge(cands, cap, tree, n, ru, rv, state_u, state_v, size_u, size_v, total):
  if size_u >= size_v:
    return try_merge(cands, cap, tree, n, rv, ru, state_v, state_u, total)
  else:
    return try_merge(cands, cap, tree, n, ru, rv, state_u, state_v, total)

def try_merge(cands, cap, tree, n, small, big, small_state, big_state, total):
  small_members = state_members(small_state)
  if cluster_conflict(small_members, tree, n, big) == 1:
    return process_candidates(cands, cap, tree, n)
  else:
    parent_state = state_with_parent(small_state, big)
    tree1 = tree_set(tree, 0, n, small, parent_state)
    big_maximum = state_maximum(big_state)
    small_maximum = state_maximum(small_state)
    if big_maximum > small_maximum:
      maximum = big_maximum
    else:
      maximum = small_maximum
    big_members = state_members(big_state)
    members = append_lists(small_members, big_members)
    merged_state = state_with_merge(big_state, total, maximum, members)
    tree2 = tree_set(tree1, 0, n, big, merged_state)
    return process_candidates(cands, cap, tree2, n)

def build_result(i, n, tree):
  if i == n:
    return []
  else:
    root = find_root(tree, n, i)
    state = tree_get(tree, 0, n, root)
    maximum = state_maximum(state)
    return List/Cons(maximum, build_result(i + 1, n, tree))
