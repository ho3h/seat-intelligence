def prog(x):
  (n, tau, mnl, cands) = x
  candidate_count = list_len(cands)
  candidates_by_pair = merge_sort(cands, candidate_count, 0)
  unique_candidates = collapse_pairs(candidates_by_pair)
  accepted = filter_accepted(unique_candidates, tau)
  accepted_count = list_len(accepted)
  ordered = merge_sort(accepted, accepted_count, 1)
  uf = build_uf(0, n)
  adjacency = build_adjacency(0, n)
  adjacency = add_constraints(mnl, adjacency, n)
  final_uf = process_edges(ordered, uf, adjacency, n)
  return make_output(final_uf, 0, n)

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def split_at(xs, k):
  if k == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (left, right) = split_at(xs.tail, k - 1)
        return (List/Cons(xs.head, left), right)

def merge_sort(xs, n, mode):
  if n < 2:
    return xs
  else:
    half = n / 2
    (left, right) = split_at(xs, half)
    sorted_left = merge_sort(left, half, mode)
    sorted_right = merge_sort(right, n - half, mode)
    return merge_sorted(sorted_left, sorted_right, mode)

def merge_sorted(left, right, mode):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if edge_before(left.head, right.head, mode):
            return List/Cons(left.head, merge_sorted(left.tail, right, mode))
          else:
            return List/Cons(right.head, merge_sorted(left, right.tail, mode))

def edge_before(a, b, mode):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if mode == 0:
    if u1 < u2:
      return 1
    else:
      if u1 > u2:
        return 0
      else:
        if v1 < v2:
          return 1
        else:
          if v1 > v2:
            return 0
          else:
            return s1 > s2
  else:
    if s1 > s2:
      return 1
    else:
      if s1 < s2:
        return 0
      else:
        if u1 < u2:
          return 1
        else:
          if u1 > u2:
            return 0
          else:
            return v1 < v2

def collapse_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      rest = skip_pair(xs.tail, u, v)
      return List/Cons(xs.head, collapse_pairs(rest))

def skip_pair(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (eu, ev, score) = xs.head
      if eu == u:
        if ev == v:
          return skip_pair(xs.tail, u, v)
        else:
          return xs
      else:
        return xs

def filter_accepted(xs, tau):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      rest = filter_accepted(xs.tail, tau)
      if score >= tau:
        return List/Cons(xs.head, rest)
      else:
        return rest

def build_uf(lo, hi):
  if lo >= hi:
    return []
  else:
    if lo + 1 == hi:
      return (lo, 1, List/Cons(lo, []), lo)
    else:
      mid = (lo + hi) / 2
      left = build_uf(lo, mid)
      right = build_uf(mid, hi)
      return (left, right)

def build_adjacency(lo, hi):
  if lo >= hi:
    return []
  else:
    if lo + 1 == hi:
      return []
    else:
      mid = (lo + hi) / 2
      left = build_adjacency(lo, mid)
      right = build_adjacency(mid, hi)
      return (left, right)

def tree_get(tree, lo, hi, index):
  if lo + 1 == hi:
    return tree
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_set(tree, lo, hi, index, value):
  if lo + 1 == hi:
    return value
  else:
    mid = (lo + hi) / 2
    (left, right) = tree
    if index < mid:
      new_left = tree_set(left, lo, mid, index, value)
      return (new_left, right)
    else:
      new_right = tree_set(right, mid, hi, index, value)
      return (left, new_right)

def add_constraints(mnl, adjacency, n):
  match mnl:
    case List/Nil:
      return adjacency
    case List/Cons:
      (a, b) = mnl.head
      neighbors_a = tree_get(adjacency, 0, n, a)
      adjacency_a = tree_set(adjacency, 0, n, a, List/Cons(b, neighbors_a))
      neighbors_b = tree_get(adjacency_a, 0, n, b)
      adjacency_b = tree_set(adjacency_a, 0, n, b, List/Cons(a, neighbors_b))
      return add_constraints(mnl.tail, adjacency_b, n)

def find_root(uf, node, n):
  record = tree_get(uf, 0, n, node)
  (parent, size, members, canonical) = record
  if parent == node:
    return node
  else:
    return find_root(uf, parent, n)

def has_neighbor_in_root(members, adjacency, uf, target_root, n):
  match members:
    case List/Nil:
      return 0
    case List/Cons:
      neighbors = tree_get(adjacency, 0, n, members.head)
      if neighbors_hit_root(neighbors, uf, target_root, n):
        return 1
      else:
        return has_neighbor_in_root(members.tail, adjacency, uf, target_root, n)

def neighbors_hit_root(neighbors, uf, target_root, n):
  match neighbors:
    case List/Nil:
      return 0
    case List/Cons:
      root = find_root(uf, neighbors.head, n)
      if root == target_root:
        return 1
      else:
        return neighbors_hit_root(neighbors.tail, uf, target_root, n)

def list_concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, list_concat(xs.tail, ys))

def union_roots(uf, root_a, root_b, n):
  record_a = tree_get(uf, 0, n, root_a)
  record_b = tree_get(uf, 0, n, root_b)
  (parent_a, size_a, members_a, canonical_a) = record_a
  (parent_b, size_b, members_b, canonical_b) = record_b
  if size_a >= size_b:
    merged_members = list_concat(members_a, members_b)
    if canonical_a >= canonical_b:
      merged_canonical = canonical_a
    else:
      merged_canonical = canonical_b
    new_big_record = (root_a, size_a + size_b, merged_members, merged_canonical)
    new_small_record = (root_a, size_b, members_b, canonical_b)
    uf1 = tree_set(uf, 0, n, root_b, new_small_record)
    return tree_set(uf1, 0, n, root_a, new_big_record)
  else:
    merged_members = list_concat(members_b, members_a)
    if canonical_a >= canonical_b:
      merged_canonical = canonical_a
    else:
      merged_canonical = canonical_b
    new_big_record = (root_b, size_a + size_b, merged_members, merged_canonical)
    new_small_record = (root_b, size_a, members_a, canonical_a)
    uf1 = tree_set(uf, 0, n, root_a, new_small_record)
    return tree_set(uf1, 0, n, root_b, new_big_record)

def process_edges(edges, uf, adjacency, n):
  match edges:
    case List/Nil:
      return uf
    case List/Cons:
      (u, v, score) = edges.head
      root_u = find_root(uf, u, n)
      root_v = find_root(uf, v, n)
      if root_u == root_v:
        return process_edges(edges.tail, uf, adjacency, n)
      else:
        record_u = tree_get(uf, 0, n, root_u)
        record_v = tree_get(uf, 0, n, root_v)
        (parent_u, size_u, members_u, canonical_u) = record_u
        (parent_v, size_v, members_v, canonical_v) = record_v
        if size_u <= size_v:
          blocked = has_neighbor_in_root(members_u, adjacency, uf, root_v, n)
        else:
          blocked = has_neighbor_in_root(members_v, adjacency, uf, root_u, n)
        if blocked == 1:
          return process_edges(edges.tail, uf, adjacency, n)
        else:
          merged = union_roots(uf, root_u, root_v, n)
          return process_edges(edges.tail, merged, adjacency, n)

def make_output(uf, i, n):
  if i >= n:
    return []
  else:
    root = find_root(uf, i, n)
    record = tree_get(uf, 0, n, root)
    (parent, size, members, canonical) = record
    return List/Cons(canonical, make_output(uf, i + 1, n))
