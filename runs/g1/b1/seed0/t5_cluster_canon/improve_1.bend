def prog(x):
  (n, pairs) = x
  parent = make_labels(0, n)
  parent2 = merge_edges(pairs, parent)
  (parent3, output) = make_output(0, n, parent2)
  return output

def make_labels(i, n):
  if i < n:
    rest = make_labels(i + 1, n)
    return List/Cons(i, rest)
  else:
    return List/Nil

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
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        rest = set_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, rest)

def find_compress(parent, x):
  p = get_at(parent, x)
  if p == x:
    return (parent, x)
  else:
    (parent2, root) = find_compress(parent, p)
    if p == root:
      return (parent2, root)
    else:
      parent3 = set_at(parent2, x, root)
      return (parent3, root)

def merge_edges(pairs, parent):
  match pairs:
    case List/Nil:
      return parent
    case List/Cons:
      (u, v) = pairs.head
      (parent1, root_u) = find_compress(parent, u)
      (parent2, root_v) = find_compress(parent1, v)
      if root_u == root_v:
        return merge_edges(pairs.tail, parent2)
      else:
        if root_u < root_v:
          parent3 = set_at(parent2, root_u, root_v)
          return merge_edges(pairs.tail, parent3)
        else:
          parent3 = set_at(parent2, root_v, root_u)
          return merge_edges(pairs.tail, parent3)

def make_output(i, n, parent):
  if i < n:
    (parent1, root) = find_compress(parent, i)
    (parent2, tail) = make_output(i + 1, n, parent1)
    return (parent2, List/Cons(root, tail))
  else:
    return (parent, List/Nil)
