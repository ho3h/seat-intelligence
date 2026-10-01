def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  return merge_edges(pairs, labels)

def make_labels(i, n):
  if i < n:
    return List/Cons(i, make_labels(i + 1, n))
  else:
    return []

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_at(xs.tail, i - 1)

def replace_label(xs, old_label, new_label):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old_label:
        return List/Cons(new_label, replace_label(xs.tail, old_label, new_label))
      else:
        return List/Cons(xs.head, replace_label(xs.tail, old_label, new_label))

def merge_edges(pairs, labels):
  match pairs:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = pairs.head
      left = get_at(labels, u)
      right = get_at(labels, v)
      if left == right:
        return merge_edges(pairs.tail, labels)
      else:
        if left < right:
          updated = replace_label(labels, right, left)
          return merge_edges(pairs.tail, updated)
        else:
          updated = replace_label(labels, left, right)
          return merge_edges(pairs.tail, updated)
