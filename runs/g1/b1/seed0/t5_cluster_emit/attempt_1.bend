def prog(x):
  (n, pairs) = x
  labels = make_labels(n, 0)
  merged_labels = process_edges(pairs, labels)
  return emit(merged_labels, 0)

def make_labels(n, i):
  if i == n:
    return []
  else:
    tail = make_labels(n, i + 1)
    return List/Cons(i, tail)

def get_label(labels, i):
  match labels:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return labels.head
      else:
        return get_label(labels.tail, i - 1)

def replace_label(labels, low, high):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = replace_label(labels.tail, low, high)
      if labels.head == low:
        return List/Cons(high, tail)
      else:
        return List/Cons(labels.head, tail)

def process_edges(pairs, labels):
  match pairs:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = pairs.head
      label_u = get_label(labels, u)
      label_v = get_label(labels, v)
      if label_u == label_v:
        return process_edges(pairs.tail, labels)
      else:
        if label_u < label_v:
          updated = replace_label(labels, label_u, label_v)
          return process_edges(pairs.tail, updated)
        else:
          updated = replace_label(labels, label_v, label_u)
          return process_edges(pairs.tail, updated)

def emit(labels, i):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = emit(labels.tail, i + 1)
      if i == labels.head:
        return tail
      else:
        return List/Cons((i, labels.head), tail)
