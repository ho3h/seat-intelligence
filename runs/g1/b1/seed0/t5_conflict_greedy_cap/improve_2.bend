def prog(x):
  (n, cap, mnl, cands) = x
  words = (n + 23) / 24
  tree = build_tree(0, n, words)
  tree1 = mark_links(mnl, tree, n)
  ordered = sort_candidates(cands)
  tree2 = process_candidates(ordered, cap, tree1, n)
  return build_result(0, n, tree2)

def make_bits(i, words, node):
  if i == words:
    return []
  else:
    if i == node / 24:
      value = 1 << (node % 24)
      return List/Cons(value, make_bits(i + 1, words, node))
    else:
      return List/Cons(0, make_bits(i + 1, words, node))

def zero_bits(words):
  if words == 0:
    return []
  else:
    return List/Cons(0, zero_bits(words - 1))

def make_state(parent, size, maximum, members, forbidden):
  return (parent, (size, (maximum, (members, forbidden))))

def build_tree(lo, hi, words):
  if lo == hi:
    return []
  else:
    if hi - lo == 1:
      return make_state(lo, 1, lo, make_bits(0, words, lo), zero_bits(words))
    else:
      mid = (lo + hi) / 2
      left = build_tree(lo, mid, words)
      right = build_tree(mid, hi, words)
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
  (members, forbidden) = rest3
  return members

def state_forbidden(state):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, forbidden) = rest3
  return forbidden

def state_with_parent(state, new_parent):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, forbidden) = rest3
  return make_state(new_parent, size, maximum, members, forbidden)

def state_with_forbidden(state, new_forbidden):
  (parent, rest) = state
  (size, rest2) = rest
  (maximum, rest3) = rest2
  (members, forbidden) = rest3
  return make_state(parent, size, maximum, members, new_forbidden)

def state_with_merge(state, new_size, new_maximum, new_members, new_forbidden):
  (parent, rest) = state
  return make_state(parent, new_size, new_maximum, new_members, new_forbidden)

def get_parent(tree, n, node):
  state = tree_get(tree, 0, n, node)
  return state_parent(state)

def find_root(tree, n, node):
  parent = get_parent(tree, n, node)
  if parent == node:
    return node
  else:
    return find_root(tree, n, parent)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def set_forbidden_bit(bits, node):
  word = node / 24
  bit = node % 24
  old = get_at(bits, word)
  new = old | (1 << bit)
  return set_at(bits, word, new)

def mark_one_link(tree, n, node, neighbor):
  state = tree_get(tree, 0, n, node)
  forbidden = state_forbidden(state)
  new_forbidden = set_forbidden_bit(forbidden, neighbor)
  new_state = state_with_forbidden(state, new_forbidden)
  return tree_set(tree, 0, n, node, new_state)

def mark_links(links, tree, n):
  match links:
    case List/Nil:
      return tree
    case List/Cons:
      (a, b) = links.head
      tree1 = mark_one_link(tree, n, a, b)
      tree2 = mark_one_link(tree1, n, b, a)
      return mark_links(links.tail, tree2, n)

def vectors_conflict(a, b):
  match a:
    case List/Nil:
      return 0
    case List/Cons:
      match b:
        case List/Nil:
          return 0
        case List/Cons:
          if (a.head & b.head) != 0:
            return 1
          else:
            return vectors_conflict(a.tail, b.tail)

def vector_or(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(a.head | b.head, vector_or(a.tail, b.tail))

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
          if vectors_conflict(state_forbidden(state_u), state_members(state_v)) == 1:
            return process_candidates(cands.tail, cap, tree, n)
          else:
            return merge_roots(cands.tail, cap, tree, n, ru, rv, state_u, state_v, size_u, size_v, total)

def merge_roots(cands, cap, tree, n, ru, rv, state_u, state_v, size_u, size_v, total):
  if size_u >= size_v:
    return merge_ordered(cands, cap, tree, n, rv, ru, state_v, state_u, total)
  else:
    return merge_ordered(cands, cap, tree, n, ru, rv, state_u, state_v, total)

def merge_ordered(cands, cap, tree, n, small, big, small_state, big_state, total):
  parent_state = state_with_parent(small_state, big)
  tree1 = tree_set(tree, 0, n, small, parent_state)
  big_maximum = state_maximum(big_state)
  small_maximum = state_maximum(small_state)
  if big_maximum > small_maximum:
    maximum = big_maximum
  else:
    maximum = small_maximum
  members = vector_or(state_members(big_state), state_members(small_state))
  forbidden = vector_or(state_forbidden(big_state), state_forbidden(small_state))
  merged_state = state_with_merge(big_state, total, maximum, members, forbidden)
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
