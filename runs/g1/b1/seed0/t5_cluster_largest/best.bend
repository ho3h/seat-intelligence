def prog(x):
  (n, pairs) = x
  labels = make_labels(n, 0)
  merged = merge_edges(pairs, labels)
  return largest_cluster(merged, 0)

def make_labels(n, i):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(n, i + 1))

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_at(xs.tail, index - 1)

def replace_all(xs, old, new):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, replace_all(xs.tail, old, new))
      else:
        return List/Cons(xs.head, replace_all(xs.tail, old, new))

def merge_edges(pairs, labels):
  match pairs:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = pairs.head
      label_u = get_at(labels, u)
      label_v = get_at(labels, v)
      if label_u == label_v:
        return merge_edges(pairs.tail, labels)
      else:
        updated = replace_all(labels, label_v, label_u)
        return merge_edges(pairs.tail, updated)

def count_value(xs, target, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == target:
        return count_value(xs.tail, target, acc + 1)
      else:
        return count_value(xs.tail, target, acc)

def largest_cluster(xs, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      size = count_value(xs, xs.head, 0)
      if size > best:
        return largest_cluster(xs.tail, size)
      else:
        return largest_cluster(xs.tail, best)
