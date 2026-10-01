def prog(x):
  (n, pairs) = x
  if n == 0:
    return 0
  else:
    labels = build_tree(0, n, 0)
    sizes = build_tree(0, n, 1)
    return process_edges(pairs, labels, sizes, n, 0)

def build_tree(lo, hi, kind):
  if hi - lo == 1:
    if kind == 0:
      return (0, lo)
    else:
      return (0, 1)
  else:
    mid = (lo + hi) / 2
    left = build_tree(lo, mid, kind)
    right = build_tree(mid, hi, kind)
    return (1, (left, right))

def tree_get(tree, lo, hi, index):
  (tag, payload) = tree
  if tag == 0:
    return payload
  else:
    (left, right) = payload
    mid = (lo + hi) / 2
    if index < mid:
      return tree_get(left, lo, mid, index)
    else:
      return tree_get(right, mid, hi, index)

def tree_set(tree, lo, hi, index, value):
  (tag, payload) = tree
  if tag == 0:
    return (0, value)
  else:
    (left, right) = payload
    mid = (lo + hi) / 2
    if index < mid:
      new_left = tree_set(left, lo, mid, index, value)
      return (1, (new_left, right))
    else:
      new_right = tree_set(right, mid, hi, index, value)
      return (1, (left, new_right))

def replace_label(tree, lo, hi, old_label, new_label):
  (tag, payload) = tree
  if tag == 0:
    if payload == old_label:
      return (0, new_label)
    else:
      return tree
  else:
    (left, right) = payload
    mid = (lo + hi) / 2
    new_left = replace_label(left, lo, mid, old_label, new_label)
    new_right = replace_label(right, mid, hi, old_label, new_label)
    return (1, (new_left, new_right))

def process_edges(edges, labels, sizes, n, answer):
  match edges:
    case List/Nil:
      return answer
    case List/Cons:
      (u, v) = edges.head
      label_u = tree_get(labels, 0, n, u)
      label_v = tree_get(labels, 0, n, v)
      if label_u == label_v:
        return process_edges(edges.tail, labels, sizes, n, answer)
      else:
        size_u = tree_get(sizes, 0, n, label_u)
        size_v = tree_get(sizes, 0, n, label_v)
        added = size_u * size_v
        if size_u < size_v:
          labels2 = replace_label(labels, 0, n, label_u, label_v)
          sizes2 = tree_set(sizes, 0, n, label_v, size_u + size_v)
          return process_edges(edges.tail, labels2, sizes2, n, answer + added)
        else:
          labels2 = replace_label(labels, 0, n, label_v, label_u)
          sizes2 = tree_set(sizes, 0, n, label_u, size_u + size_v)
          return process_edges(edges.tail, labels2, sizes2, n, answer + added)
