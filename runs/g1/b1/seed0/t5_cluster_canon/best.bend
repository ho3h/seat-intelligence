def prog(x):
  (n, pairs) = x
  if n == 0:
    return List/Nil
  else:
    parent = make_tree(0, n)
    parent2 = merge_edges(pairs, parent, n)
    (parent3, output) = make_output(0, n, parent2, n)
    return output

def make_tree(lo, hi):
  if hi - lo == 1:
    return (lo, lo, 1)
  else:
    mid = lo + ((hi - lo) / 2)
    left = make_tree(lo, mid)
    right = make_tree(mid, hi)
    return (left, right)

def get_tree(tree, lo, hi, idx):
  if hi - lo == 1:
    return tree
  else:
    (left, right) = tree
    mid = lo + ((hi - lo) / 2)
    if idx < mid:
      return get_tree(left, lo, mid, idx)
    else:
      return get_tree(right, mid, hi, idx)

def set_tree(tree, lo, hi, idx, value):
  if hi - lo == 1:
    return value
  else:
    (left, right) = tree
    mid = lo + ((hi - lo) / 2)
    if idx < mid:
      left2 = set_tree(left, lo, mid, idx, value)
      return (left2, right)
    else:
      right2 = set_tree(right, mid, hi, idx, value)
      return (left, right2)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def find_compress(parent, x, n):
  (p, largest, size) = get_tree(parent, 0, n, x)
  if p == x:
    return (parent, x, largest, size)
  else:
    (parent2, root, root_largest, root_size) = find_compress(parent, p, n)
    parent3 = set_tree(parent2, 0, n, x, (root, largest, size))
    return (parent3, root, root_largest, root_size)

def merge_edges(pairs, parent, n):
  match pairs:
    case List/Nil:
      return parent
    case List/Cons:
      (u, v) = pairs.head
      (parent1, root_u, max_u, size_u) = find_compress(parent, u, n)
      (parent2, root_v, max_v, size_v) = find_compress(parent1, v, n)
      if root_u == root_v:
        return merge_edges(pairs.tail, parent2, n)
      else:
        largest = max2(max_u, max_v)
        merged_size = size_u + size_v
        if size_u < size_v:
          parent3 = set_tree(parent2, 0, n, root_v, (root_v, largest, merged_size))
          parent4 = set_tree(parent3, 0, n, root_u, (root_v, largest, size_u))
          return merge_edges(pairs.tail, parent4, n)
        else:
          parent3 = set_tree(parent2, 0, n, root_u, (root_u, largest, merged_size))
          parent4 = set_tree(parent3, 0, n, root_v, (root_u, largest, size_v))
          return merge_edges(pairs.tail, parent4, n)

def make_output(i, n, parent, total):
  if i < total:
    (parent1, root, largest, size) = find_compress(parent, i, total)
    (parent2, tail) = make_output(i + 1, n, parent1, total)
    return (parent2, List/Cons(largest, tail))
  else:
    return (parent, List/Nil)
