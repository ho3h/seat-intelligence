type IndexTree: Empty | Leaf { value } | Branch { left_size, left, right }

def prog(x):
  (c, edges) = x
  n = length(c)
  (tree, _) = build_index(c, n)
  mapped = rewrite_edges(tree, edges, [])
  return quick_sort_edges(mapped)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def build_index(xs, n):
  if n == 0:
    return (IndexTree/Empty, xs)
  else:
    if n == 1:
      match xs:
        case List/Nil:
          return (IndexTree/Empty, xs)
        case List/Cons:
          return (IndexTree/Leaf(xs.head), xs.tail)
    else:
      left_size = n / 2
      (left, rest) = build_index(xs, left_size)
      (right, rest2) = build_index(rest, n - left_size)
      return (IndexTree/Branch(left_size, left, right), rest2)

def index_lookup(tree, i):
  match tree:
    case IndexTree/Empty:
      return 0
    case IndexTree/Leaf:
      return tree.value
    case IndexTree/Branch:
      if i < tree.left_size:
        return index_lookup(tree.left, i)
      else:
        return index_lookup(tree.right, i - tree.left_size)

def rewrite_edges(tree, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, w) = edges.head
      cu = index_lookup(tree, u)
      cv = index_lookup(tree, v)
      if cu == cv:
        return rewrite_edges(tree, edges.tail, acc)
      else:
        if cu < cv:
          return rewrite_edges(tree, edges.tail, List/Cons((cu, cv, w), acc))
        else:
          return rewrite_edges(tree, edges.tail, List/Cons((cv, cu, w), acc))

def pair_le_edges(a, b):
  (ax, ay, _) = a
  (bx, by, _) = b
  if ax < bx:
    return 1
  else:
    if ax == bx:
      if ay <= by:
        return 1
      else:
        return 0
    else:
      return 0

def median_edge(a, b, c):
  if pair_le_edges(a, b) == 1:
    if pair_le_edges(b, c) == 1:
      return b
    else:
      if pair_le_edges(a, c) == 1:
        return c
      else:
        return a
  else:
    if pair_le_edges(a, c) == 1:
      return a
    else:
      if pair_le_edges(b, c) == 1:
        return c
      else:
        return b

def middle_and_last(fast, slow, last):
  match fast:
    case List/Nil:
      return (slow.head, last)
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return (slow.head, fast.head)
        case List/Cons:
          return middle_and_last(fast.tail.tail, slow.tail, fast.tail.head)

def partition_edges(xs, px, py, less, greater, total):
  match xs:
    case List/Nil:
      return (less, (total, greater))
    case List/Cons:
      (x, y, w) = xs.head
      if x == px:
        if y == py:
          return partition_edges(xs.tail, px, py, less, greater, total + w)
        else:
          if y < py:
            return partition_edges(xs.tail, px, py, List/Cons(xs.head, less), greater, total)
          else:
            return partition_edges(xs.tail, px, py, less, List/Cons(xs.head, greater), total)
      else:
        if x < px:
          return partition_edges(xs.tail, px, py, List/Cons(xs.head, less), greater, total)
        else:
          return partition_edges(xs.tail, px, py, less, List/Cons(xs.head, greater), total)

def quick_sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (middle, last) = middle_and_last(xs, xs, 0)
          pivot = median_edge(xs.head, middle, last)
          (px, py, _) = pivot
          (less, (total, greater)) = partition_edges(xs, px, py, [], [], 0)
          left = quick_sort_edges(less)
          right = quick_sort_edges(greater)
          return append_edges(left, List/Cons((px, py, total), right))

def append_edges(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append_edges(xs.tail, ys))
