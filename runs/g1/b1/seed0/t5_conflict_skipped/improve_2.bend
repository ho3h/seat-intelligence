type ClusterTree: Leaf { item } | Branch { left, right }

def prog(x):
  (n, cap, mnl, cands) = x
  words = (n + 23) / 24
  zero_bits = make_zero_bits(words)
  span = tree_span(n, 1)
  tree = make_tree(0, span, n, zero_bits)
  tree = add_constraints(mnl, tree, span)
  ordered = merge_sort(cands)
  return process(ordered, tree, span, cap, [])

def tree_span(n, span):
  if span >= n:
    return span
  else:
    return tree_span(n, span * 2)

def make_zero_bits(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, make_zero_bits(count - 1))

def bit_set(bits, index):
  word_index = index / 24
  bit_index = index % 24
  word = list_at(bits, word_index)
  return list_set(bits, word_index, word | (1 << bit_index))

def list_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return list_at(xs.tail, index - 1)

def list_set(xs, index, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, list_set(xs.tail, index - 1, value))

def make_tree(start, span, n, zero_bits):
  if span == 1:
    if start < n:
      members = bit_set(zero_bits, start)
      return ClusterTree/Leaf((start, (members, zero_bits, 1)))
    else:
      return ClusterTree/Leaf((0, (zero_bits, zero_bits, 0)))
  else:
    half = span / 2
    left = make_tree(start, half, n, zero_bits)
    right = make_tree(start + half, half, n, zero_bits)
    return ClusterTree/Branch(left, right)

def tree_get(tree, index, span):
  match tree:
    case ClusterTree/Leaf:
      return tree.item
    case ClusterTree/Branch:
      half = span / 2
      if index < half:
        return tree_get(tree.left, index, half)
      else:
        return tree_get(tree.right, index - half, half)

def tree_set(tree, index, span, item):
  match tree:
    case ClusterTree/Leaf:
      return ClusterTree/Leaf(item)
    case ClusterTree/Branch:
      half = span / 2
      if index < half:
        left = tree_set(tree.left, index, half, item)
        return ClusterTree/Branch(left, tree.right)
      else:
        right = tree_set(tree.right, index - half, half, item)
        return ClusterTree/Branch(tree.left, right)

def add_constraints(mnl, tree, span):
  match mnl:
    case List/Nil:
      return tree
    case List/Cons:
      (a, b) = mnl.head
      item_a = tree_get(tree, a, span)
      (parent_a, state_a) = item_a
      (members_a, forbidden_a, size_a) = state_a
      state_a = (members_a, bit_set(forbidden_a, b), size_a)
      tree = tree_set(tree, a, span, (parent_a, state_a))

      item_b = tree_get(tree, b, span)
      (parent_b, state_b) = item_b
      (members_b, forbidden_b, size_b) = state_b
      state_b = (members_b, bit_set(forbidden_b, a), size_b)
      tree = tree_set(tree, b, span, (parent_b, state_b))
      return add_constraints(mnl.tail, tree, span)

def find_root(tree, index, span):
  item = tree_get(tree, index, span)
  (parent, state) = item
  if parent == index:
    return index
  else:
    return find_root(tree, parent, span)

def bit_or(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(a.head | b.head, bit_or(a.tail, b.tail))

def has_intersection(a, b):
  match a:
    case List/Nil:
      return 0
    case List/Cons:
      if (a.head & b.head) != 0:
        return 1
      else:
        return has_intersection(a.tail, b.tail)

def candidate_precedes(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
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
          if v1 < v2:
            return 1
          else:
            return 0

def split_alternating(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alternating(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if candidate_precedes(a.head, b.head) == 1:
            return List/Cons(a.head, merge_sorted(a.tail, b))
          else:
            return List/Cons(b.head, merge_sorted(a, b.tail))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternating(xs)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_sorted(sorted_left, sorted_right)

def reverse_pairs(xs):
  return reverse_pairs_acc(xs, [])

def reverse_pairs_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_pairs_acc(xs.tail, List/Cons(xs.head, acc))

def process(cands, tree, span, cap, skipped_rev):
  match cands:
    case List/Nil:
      return reverse_pairs(skipped_rev)
    case List/Cons:
      (u, v, score) = cands.head
      root_u = find_root(tree, u, span)
      root_v = find_root(tree, v, span)
      if root_u == root_v:
        return process(cands.tail, tree, span, cap, skipped_rev)
      else:
        item_u = tree_get(tree, root_u, span)
        item_v = tree_get(tree, root_v, span)
        (parent_u, state_u) = item_u
        (parent_v, state_v) = item_v
        (members_u, forbidden_u, size_u) = state_u
        (members_v, forbidden_v, size_v) = state_v
        if size_u + size_v > cap:
          skipped_rev = List/Cons((u, v), skipped_rev)
          return process(cands.tail, tree, span, cap, skipped_rev)
        else:
          if has_intersection(forbidden_u, members_v) == 1:
            skipped_rev = List/Cons((u, v), skipped_rev)
            return process(cands.tail, tree, span, cap, skipped_rev)
          else:
            members = bit_or(members_u, members_v)
            forbidden = bit_or(forbidden_u, forbidden_v)
            merged_state = (members, forbidden, size_u + size_v)
            if size_u >= size_v:
              tree = tree_set(tree, root_v, span, (root_u, state_v))
              tree = tree_set(tree, root_u, span, (root_u, merged_state))
            else:
              tree = tree_set(tree, root_u, span, (root_v, state_u))
              tree = tree_set(tree, root_v, span, (root_v, merged_state))
            return process(cands.tail, tree, span, cap, skipped_rev)
