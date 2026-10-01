def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  merged = merge_edges(pairs, labels)
  return collect_roots(merged, merged, 0)

def make_labels(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(i + 1, n))

def get_label(labels, i):
  match labels:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return labels.head
      else:
        return get_label(labels.tail, i - 1)

def replace_label(labels, old, new):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = replace_label(labels.tail, old, new)
      if labels.head == old:
        return List/Cons(new, tail)
      else:
        return List/Cons(labels.head, tail)

def merge_edges(edges, labels):
  match edges:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = edges.head
      label_u = get_label(labels, u)
      label_v = get_label(labels, v)
      if label_u == label_v:
        return merge_edges(edges.tail, labels)
      else:
        if label_u < label_v:
          updated = replace_label(labels, label_v, label_u)
        else:
          updated = replace_label(labels, label_u, label_v)
        return merge_edges(edges.tail, updated)

def collect_members(labels, i, target):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = collect_members(labels.tail, i + 1, target)
      if labels.head == target:
        return List/Cons(i, tail)
      else:
        return tail

def collect_roots(rest, labels, i):
  match rest:
    case List/Nil:
      return []
    case List/Cons:
      tail = collect_roots(rest.tail, labels, i + 1)
      if rest.head == i:
        group = collect_members(labels, 0, i)
        return List/Cons(group, tail)
      else:
        return tail
