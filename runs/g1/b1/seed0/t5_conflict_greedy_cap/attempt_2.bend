def prog(x):
  (n, cap, mnl, cands) = x
  parent = make_nodes(0, n)
  sizes = make_ones(0, n)
  maxima = make_nodes(0, n)
  members = make_singletons(0, n)
  adjacency = make_empty_lists(0, n)
  adjacency = mark_links(mnl, adjacency)
  ordered = sort_candidates(cands)
  (parent, sizes, maxima, members) = process_candidates(ordered, cap, parent, sizes, maxima, members, adjacency)
  return build_result(0, n, parent, maxima)

def make_nodes(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_nodes(i + 1, n))

def make_ones(i, n):
  if i == n:
    return []
  else:
    return List/Cons(1, make_ones(i + 1, n))

def make_singletons(i, n):
  if i == n:
    return []
  else:
    return List/Cons(List/Cons(i, []), make_singletons(i + 1, n))

def make_empty_lists(i, n):
  if i == n:
    return []
  else:
    return List/Cons([], make_empty_lists(i + 1, n))

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

def find_root(parent, node):
  p = get_at(parent, node)
  if p == node:
    return node
  else:
    return find_root(parent, p)

def append_lists(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_lists(a.tail, b))

def mark_links(links, adjacency):
  match links:
    case List/Nil:
      return adjacency
    case List/Cons:
      (a, b) = links.head
      a_links = get_at(adjacency, a)
      b_links = get_at(adjacency, b)
      adjacency1 = set_at(adjacency, a, List/Cons(b, a_links))
      adjacency2 = set_at(adjacency1, b, List/Cons(a, b_links))
      return mark_links(links.tail, adjacency2)

def neighbor_conflict(neighbors, parent, other_root):
  match neighbors:
    case List/Nil:
      return 0
    case List/Cons:
      root = find_root(parent, neighbors.head)
      if root == other_root:
        return 1
      else:
        return neighbor_conflict(neighbors.tail, parent, other_root)

def cluster_conflict(nodes, adjacency, parent, other_root):
  match nodes:
    case List/Nil:
      return 0
    case List/Cons:
      neighbors = get_at(adjacency, nodes.head)
      if neighbor_conflict(neighbors, parent, other_root) == 1:
        return 1
      else:
        return cluster_conflict(nodes.tail, adjacency, parent, other_root)

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

def process_candidates(cands, cap, parent, sizes, maxima, members, adjacency):
  match cands:
    case List/Nil:
      return (parent, sizes, maxima, members)
    case List/Cons:
      (u, v, score) = cands.head
      ru = find_root(parent, u)
      rv = find_root(parent, v)
      if ru == rv:
        return process_candidates(cands.tail, cap, parent, sizes, maxima, members, adjacency)
      else:
        size_u = get_at(sizes, ru)
        size_v = get_at(sizes, rv)
        total = size_u + size_v
        if total > cap:
          return process_candidates(cands.tail, cap, parent, sizes, maxima, members, adjacency)
        else:
          return attempt_merge(cands.tail, cap, parent, sizes, maxima, members, adjacency, ru, rv, size_u, size_v, total)

def attempt_merge(cands, cap, parent, sizes, maxima, members, adjacency, ru, rv, size_u, size_v, total):
  if size_u >= size_v:
    big = ru
    small = rv
  else:
    big = rv
    small = ru
  blocked = cluster_conflict(get_at(members, small), adjacency, parent, big)
  if blocked == 1:
    return process_candidates(cands, cap, parent, sizes, maxima, members, adjacency)
  else:
    parent1 = set_at(parent, small, big)
    sizes1 = set_at(sizes, big, total)
    max_big = get_at(maxima, big)
    max_small = get_at(maxima, small)
    if max_big > max_small:
      max_value = max_big
    else:
      max_value = max_small
    maxima1 = set_at(maxima, big, max_value)
    big_members = get_at(members, big)
    small_members = get_at(members, small)
    combined = append_lists(small_members, big_members)
    members1 = set_at(members, big, combined)
    return process_candidates(cands, cap, parent1, sizes1, maxima1, members1, adjacency)

def build_result(i, n, parent, maxima):
  if i == n:
    return []
  else:
    root = find_root(parent, i)
    value = get_at(maxima, root)
    return List/Cons(value, build_result(i + 1, n, parent, maxima))
