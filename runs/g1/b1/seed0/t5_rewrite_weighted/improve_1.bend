type IndexTree: Empty | Leaf { value } | Branch { left_size, left, right }

def prog(x):
  (c, edges) = x
  n = length(c)
  (tree, _) = build_index(c, n)
  mapped = rewrite_edges(tree, edges, [])
  sorted = sort_edges(mapped)
  return aggregate(sorted, 0, 0, 0, 0, [])

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

def split_halves(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_halves(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_halves(xs)
          return merge_sorted(sort_edges(left), sort_edges(right))

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          (ax, ay, aw) = a.head
          (bx, by, bw) = b.head
          if ax < bx:
            return List/Cons(a.head, merge_sorted(a.tail, b))
          else:
            if ax == bx:
              if ay <= by:
                return List/Cons(a.head, merge_sorted(a.tail, b))
              else:
                return List/Cons(b.head, merge_sorted(a, b.tail))
            else:
              return List/Cons(b.head, merge_sorted(a, b.tail))

def aggregate(xs, has_current, current_x, current_y, total, out):
  match xs:
    case List/Nil:
      if has_current == 0:
        return reverse(out)
      else:
        return reverse(List/Cons((current_x, current_y, total), out))
    case List/Cons:
      (x, y, w) = xs.head
      if has_current == 0:
        return aggregate(xs.tail, 1, x, y, w, out)
      else:
        if x == current_x:
          if y == current_y:
            return aggregate(xs.tail, 1, current_x, current_y, total + w, out)
          else:
            return aggregate(xs.tail, 1, x, y, w, List/Cons((current_x, current_y, total), out))
        else:
          return aggregate(xs.tail, 1, x, y, w, List/Cons((current_x, current_y, total), out))

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
