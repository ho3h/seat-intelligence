type UF: Leaf { parent, size, canon } | Node { left, right }

def prog(x):
  (n, tau, mnl, cands, edges) = x
  cap = capacity(n, 1)
  uf = build_uf(0, cap, n)
  pair_sorted = sort_candidates(cands)
  accepted_rev = collect_candidates(pair_sorted, tau, 0, 0, 0, 0, [])
  accepted = reverse_candidates(accepted_rev)
  ordered = sort_by_priority(accepted)
  final_uf = process_pairs(ordered, mnl, uf, cap)
  canonical = make_canonical(final_uf, 0, n, cap)
  rewritten = rewrite_edges(edges, final_uf, cap, [])
  sorted_edges = sort_edges(rewritten)
  distinct_rev = unique_edges(sorted_edges, [])
  return (canonical, reverse_edges(distinct_rev))

def capacity(n, cap):
  if cap >= n:
    return cap
  else:
    return capacity(n, cap * 2)

def build_uf(start, span, n):
  if span == 1:
    if start < n:
      return UF/Leaf(start, 1, start)
    else:
      return UF/Leaf(0, 0, 0)
  else:
    half = span / 2
    left = build_uf(start, half, n)
    right = build_uf(start + half, half, n)
    return UF/Node(left, right)

def get_uf(tree, index, span):
  match tree:
    case UF/Leaf:
      return (tree.parent, tree.size, tree.canon)
    case UF/Node:
      half = span / 2
      if index < half:
        return get_uf(tree.left, index, half)
      else:
        return get_uf(tree.right, index - half, half)

def set_uf(tree, index, span, parent, size, canon):
  match tree:
    case UF/Leaf:
      return UF/Leaf(parent, size, canon)
    case UF/Node:
      half = span / 2
      if index < half:
        return UF/Node(set_uf(tree.left, index, half, parent, size, canon), tree.right)
      else:
        return UF/Node(tree.left, set_uf(tree.right, index - half, half, parent, size, canon))

def find_root(tree, index, span):
  (parent, size, canon) = get_uf(tree, index, span)
  if parent == index:
    return index
  else:
    return find_root(tree, parent, span)

def canonical_node(tree, index, span):
  root = find_root(tree, index, span)
  (parent, size, canon) = get_uf(tree, root, span)
  return canon

def make_canonical(tree, index, n, span):
  if index == n:
    return []
  else:
    canon = canonical_node(tree, index, span)
    return List/Cons(canon, make_canonical(tree, index + 1, n, span))

def split_candidates(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_candidates(xs.tail)
      return (List/Cons(xs.head, right), left)

def candidate_pair_before(a, b):
  (u, v, score) = a
  (x, y, other_score) = b
  if u < x:
    return 1
  else:
    if u == x:
      if v <= y:
        return 1
      else:
        return 0
    else:
      return 0

def merge_candidates(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if candidate_pair_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_candidates(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_candidates(xs, ys.tail))

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_candidates(xs)
          return merge_candidates(sort_candidates(left), sort_candidates(right))

def flush_candidate(acc, tau, have, u, v, score):
  if have == 1:
    if score >= tau:
      return List/Cons((u, v, score), acc)
    else:
      return acc
  else:
    return acc

def collect_candidates(xs, tau, have, u, v, best, acc):
  match xs:
    case List/Nil:
      return flush_candidate(acc, tau, have, u, v, best)
    case List/Cons:
      (a, b, score) = xs.head
      if have == 0:
        return collect_candidates(xs.tail, tau, 1, a, b, score, acc)
      else:
        if a == u:
          if b == v:
            if score > best:
              return collect_candidates(xs.tail, tau, 1, u, v, score, acc)
            else:
              return collect_candidates(xs.tail, tau, 1, u, v, best, acc)
          else:
            updated = flush_candidate(acc, tau, have, u, v, best)
            return collect_candidates(xs.tail, tau, 1, a, b, score, updated)
        else:
          updated = flush_candidate(acc, tau, have, u, v, best)
          return collect_candidates(xs.tail, tau, 1, a, b, score, updated)

def reverse_candidates(xs):
  return reverse_candidates_go(xs, [])

def reverse_candidates_go(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_candidates_go(xs.tail, List/Cons(xs.head, acc))

def priority_before(a, b):
  (u, v, score) = a
  (x, y, other_score) = b
  if score > other_score:
    return 1
  else:
    if score == other_score:
      if u < x:
        return 1
      else:
        if u == x:
          if v <= y:
            return 1
          else:
            return 0
        else:
          return 0
    else:
      return 0

def split_priority(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_priority(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_priority(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if priority_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_priority(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_priority(xs, ys.tail))

def sort_by_priority(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_priority(xs)
          return merge_priority(sort_by_priority(left), sort_by_priority(right))

def has_conflict(mnl, tree, span, ra, rb):
  match mnl:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = mnl.head
      root_a = find_root(tree, a, span)
      root_b = find_root(tree, b, span)
      if root_a == ra:
        if root_b == rb:
          return 1
        else:
          return has_conflict(mnl.tail, tree, span, ra, rb)
      else:
        if root_a == rb:
          if root_b == ra:
            return 1
          else:
            return has_conflict(mnl.tail, tree, span, ra, rb)
        else:
          return has_conflict(mnl.tail, tree, span, ra, rb)

def merge_roots(tree, span, ra, rb, size_a, size_b, canon_a, canon_b):
  if canon_a > canon_b:
    canon = canon_a
  else:
    canon = canon_b
  if size_a <= size_b:
    (parent_a, old_size_a, old_canon_a) = get_uf(tree, ra, span)
    updated_a = set_uf(tree, ra, span, rb, old_size_a, old_canon_a)
    (parent_b, old_size_b, old_canon_b) = get_uf(updated_a, rb, span)
    return set_uf(updated_a, rb, span, parent_b, size_a + size_b, canon)
  else:
    (parent_b, old_size_b, old_canon_b) = get_uf(tree, rb, span)
    updated_b = set_uf(tree, rb, span, ra, old_size_b, old_canon_b)
    (parent_a, old_size_a, old_canon_a) = get_uf(updated_b, ra, span)
    return set_uf(updated_b, ra, span, parent_a, size_a + size_b, canon)

def process_pairs(pairs, mnl, tree, span):
  match pairs:
    case List/Nil:
      return tree
    case List/Cons:
      (u, v, score) = pairs.head
      ra = find_root(tree, u, span)
      rb = find_root(tree, v, span)
      if ra == rb:
        return process_pairs(pairs.tail, mnl, tree, span)
      else:
        conflict = has_conflict(mnl, tree, span, ra, rb)
        if conflict == 1:
          return process_pairs(pairs.tail, mnl, tree, span)
        else:
          (parent_a, size_a, canon_a) = get_uf(tree, ra, span)
          (parent_b, size_b, canon_b) = get_uf(tree, rb, span)
          updated = merge_roots(tree, span, ra, rb, size_a, size_b, canon_a, canon_b)
          return process_pairs(pairs.tail, mnl, updated, span)

def rewrite_edges(edges, tree, span, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      a = canonical_node(tree, u, span)
      b = canonical_node(tree, v, span)
      if a == b:
        return rewrite_edges(edges.tail, tree, span, acc)
      else:
        if a < b:
          return rewrite_edges(edges.tail, tree, span, List/Cons((a, b), acc))
        else:
          return rewrite_edges(edges.tail, tree, span, List/Cons((b, a), acc))

def split_edges(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_edges(xs.tail)
      return (List/Cons(xs.head, right), left)

def edge_before(a, b):
  (u, v) = a
  (x, y) = b
  if u < x:
    return 1
  else:
    if u == x:
      if v <= y:
        return 1
      else:
        return 0
    else:
      return 0

def merge_edges(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if edge_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_edges(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_edges(xs, ys.tail))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_edges(xs)
          return merge_edges(sort_edges(left), sort_edges(right))

def unique_edges(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return List/Cons(xs.head, acc)
        case List/Cons:
          if xs.head == xs.tail.head:
            return unique_edges(xs.tail, acc)
          else:
            return unique_edges(xs.tail, List/Cons(xs.head, acc))

def reverse_edges(xs):
  return reverse_edges_go(xs, [])

def reverse_edges_go(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_edges_go(xs.tail, List/Cons(xs.head, acc))
