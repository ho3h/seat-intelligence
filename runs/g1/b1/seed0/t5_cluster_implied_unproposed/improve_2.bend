def make_parent_tree(lo, hi):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return lo
    else:
      mid = lo + (hi - lo) / 2
      left = make_parent_tree(lo, mid)
      right = make_parent_tree(mid, hi)
      return (left, right)

def make_size_tree(lo, hi):
  if lo == hi:
    return 0
  else:
    if hi - lo == 1:
      return 1
    else:
      mid = lo + (hi - lo) / 2
      left = make_size_tree(lo, mid)
      right = make_size_tree(mid, hi)
      return (left, right)

def tree_get(tree, lo, hi, index):
  if hi - lo == 1:
    return tree
  else:
    mid = lo + (hi - lo) / 2
    (left, right) = tree
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_put(tree, lo, hi, index, value):
  if hi - lo == 1:
    return value
  else:
    mid = lo + (hi - lo) / 2
    (left, right) = tree
    if index < mid:
      left2 = tree_put(left, lo, mid, index, value)
      return (left2, right)
    else:
      right2 = tree_put(right, mid, hi, index, value)
      return (left, right2)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def split_pairs(xs, count):
  if count == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (left, right) = split_pairs(xs.tail, count - 1)
        return (List/Cons(xs.head, left), right)

def merge_pairs(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          (lu, lv) = left.head
          (ru, rv) = right.head
          if lu < ru:
            return List/Cons(left.head, merge_pairs(left.tail, right))
          else:
            if lu == ru:
              if lv <= rv:
                return List/Cons(left.head, merge_pairs(left.tail, right))
              else:
                return List/Cons(right.head, merge_pairs(left, right.tail))
            else:
              return List/Cons(right.head, merge_pairs(left, right.tail))

def sort_pairs(xs, count):
  if count < 2:
    return xs
  else:
    half = count / 2
    (left, right) = split_pairs(xs, half)
    sorted_left = sort_pairs(left, half)
    sorted_right = sort_pairs(right, count - half)
    return merge_pairs(sorted_left, sorted_right)

def find_root(parents, n, node):
  parent = tree_get(parents, 0, n, node)
  if parent == node:
    return node
  else:
    return find_root(parents, n, parent)

def process_unique(u, v, parents, sizes, n, distinct):
  root_u = find_root(parents, n, u)
  root_v = find_root(parents, n, v)
  if root_u == root_v:
    return (parents, sizes, distinct + 1)
  else:
    size_u = tree_get(sizes, 0, n, root_u)
    size_v = tree_get(sizes, 0, n, root_v)
    if size_u < size_v:
      parents2 = tree_put(parents, 0, n, root_u, root_v)
      sizes2 = tree_put(sizes, 0, n, root_v, size_u + size_v)
      return (parents2, sizes2, distinct + 1)
    else:
      parents2 = tree_put(parents, 0, n, root_v, root_u)
      sizes2 = tree_put(sizes, 0, n, root_u, size_u + size_v)
      return (parents2, sizes2, distinct + 1)

def process_sorted(edges, parents, sizes, n, has_prev, prev_u, prev_v, distinct):
  match edges:
    case List/Nil:
      return (parents, sizes, distinct)
    case List/Cons:
      (u, v) = edges.head
      if has_prev == 0:
        (parents2, sizes2, distinct2) = process_unique(u, v, parents, sizes, n, distinct)
      else:
        if u == prev_u:
          if v == prev_v:
            parents2 = parents
            sizes2 = sizes
            distinct2 = distinct
          else:
            (parents2, sizes2, distinct2) = process_unique(u, v, parents, sizes, n, distinct)
        else:
          (parents2, sizes2, distinct2) = process_unique(u, v, parents, sizes, n, distinct)
      return process_sorted(edges.tail, parents2, sizes2, n, 1, u, v, distinct2)

def sum_root_pairs(parents, sizes, n, i, total):
  if i == n:
    return total
  else:
    parent = tree_get(parents, 0, n, i)
    if parent == i:
      size = tree_get(sizes, 0, n, i)
      pairs = (size * (size - 1)) / 2
      return sum_root_pairs(parents, sizes, n, i + 1, total + pairs)
    else:
      return sum_root_pairs(parents, sizes, n, i + 1, total)

def prog(x):
  (n, edges) = x
  count = list_length(edges)
  sorted_edges = sort_pairs(edges, count)
  parents = make_parent_tree(0, n)
  sizes = make_size_tree(0, n)
  (final_parents, final_sizes, distinct) = process_sorted(sorted_edges, parents, sizes, n, 0, 0, 0, 0)
  total = sum_root_pairs(final_parents, final_sizes, n, 0, 0)
  return total - distinct
