def prog(x):
  (n, k, pairs) = x
  labels = make_labels(0, n)
  final_labels = merge_edges(pairs, labels)
  if k <= 1:
    return count_roots_all(0, n, final_labels, 0)
  else:
    return count_roots(0, n, final_labels, k, 0)

def make_labels(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(i + 1, n))

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def get_pair(xs, i, u, v, a):
  match xs:
    case List/Nil:
      return (a, 0)
    case List/Cons:
      if i == v:
        return (a, xs.head)
      else:
        if i == u:
          return get_pair(xs.tail, i + 1, u, v, xs.head)
        else:
          return get_pair(xs.tail, i + 1, u, v, a)

def replace_all(xs, old, new):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, replace_all(xs.tail, old, new))
      else:
        return List/Cons(xs.head, replace_all(xs.tail, old, new))

def merge_edges(edges, labels):
  match edges:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = edges.head
      (a, b) = get_pair(labels, 0, u, v, 0)
      if a == b:
        return merge_edges(edges.tail, labels)
      else:
        next_labels = replace_all(labels, b, a)
        return merge_edges(edges.tail, next_labels)

def count_label(xs, label, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == label:
        return count_label(xs.tail, label, acc + 1)
      else:
        return count_label(xs.tail, label, acc)

def count_roots_all(i, n, labels, acc):
  if i == n:
    return acc
  else:
    label = at(labels, i)
    if label == i:
      return count_roots_all(i + 1, n, labels, acc + 1)
    else:
      return count_roots_all(i + 1, n, labels, acc)

def count_roots(i, n, labels, k, acc):
  if i == n:
    return acc
  else:
    label = at(labels, i)
    if label == i:
      size = count_label(labels, label, 0)
      if size >= k:
        return count_roots(i + 1, n, labels, k, acc + 1)
      else:
        return count_roots(i + 1, n, labels, k, acc)
    else:
      return count_roots(i + 1, n, labels, k, acc)
