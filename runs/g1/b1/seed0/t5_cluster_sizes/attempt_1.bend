def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  merged = process_edges(pairs, labels)
  return collect_sizes(0, n, merged)

def make_labels(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(i + 1, n))

def nth(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def relabel(xs, old, new):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, relabel(xs.tail, old, new))
      else:
        return List/Cons(xs.head, relabel(xs.tail, old, new))

def process_edges(edges, labels):
  match edges:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = edges.head
      root_u = nth(labels, u)
      root_v = nth(labels, v)
      if root_u == root_v:
        return process_edges(edges.tail, labels)
      else:
        if root_u < root_v:
          updated = relabel(labels, root_u, root_v)
          return process_edges(edges.tail, updated)
        else:
          updated = relabel(labels, root_v, root_u)
          return process_edges(edges.tail, updated)

def count_label(xs, target, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == target:
        return count_label(xs.tail, target, acc + 1)
      else:
        return count_label(xs.tail, target, acc)

def collect_sizes(i, n, labels):
  if i == n:
    return []
  else:
    size = count_label(labels, i, 0)
    rest = collect_sizes(i + 1, n, labels)
    if size == 0:
      return rest
    else:
      return List/Cons(size, rest)
