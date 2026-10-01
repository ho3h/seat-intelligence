def prog(x):
  (n, tau, mnl, cands) = x
  by_pair = merge_sort(cands, list_len(cands), 0)
  unique = collapse_pairs(by_pair)
  accepted = filter_accepted(unique, tau)
  ordered = merge_sort(accepted, list_len(accepted), 1)
  labels = make_labels(0, n)
  return process_edges(ordered, labels, mnl)

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def split_at(xs, k):
  if k == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (left, right) = split_at(xs.tail, k - 1)
        return (List/Cons(xs.head, left), right)

def merge_sort(xs, n, mode):
  if n < 2:
    return xs
  else:
    half = n / 2
    (left, right) = split_at(xs, half)
    sorted_left = merge_sort(left, half, mode)
    sorted_right = merge_sort(right, n - half, mode)
    return merge_sorted(sorted_left, sorted_right, mode)

def merge_sorted(left, right, mode):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if edge_before(left.head, right.head, mode):
            return List/Cons(left.head, merge_sorted(left.tail, right, mode))
          else:
            return List/Cons(right.head, merge_sorted(left, right.tail, mode))

def edge_before(a, b, mode):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if mode == 0:
    if u1 < u2:
      return 1
    else:
      if u1 > u2:
        return 0
      else:
        if v1 < v2:
          return 1
        else:
          if v1 > v2:
            return 0
          else:
            return s1 > s2
  else:
    if s1 > s2:
      return 1
    else:
      if s1 < s2:
        return 0
      else:
        if u1 < u2:
          return 1
        else:
          if u1 > u2:
            return 0
          else:
            return v1 < v2

def collapse_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      rest = skip_pair(xs.tail, u, v)
      return List/Cons(xs.head, collapse_pairs(rest))

def skip_pair(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (eu, ev, score) = xs.head
      if eu == u:
        if ev == v:
          return skip_pair(xs.tail, u, v)
        else:
          return xs
      else:
        return xs

def filter_accepted(xs, tau):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      rest = filter_accepted(xs.tail, tau)
      if score >= tau:
        return List/Cons(xs.head, rest)
      else:
        return rest

def make_labels(i, n):
  if i >= n:
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

def process_edges(edges, labels, mnl):
  match edges:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = edges.head
      label_u = get_label(labels, u)
      label_v = get_label(labels, v)
      if label_u == label_v:
        return process_edges(edges.tail, labels, mnl)
      else:
        if has_crossing_link(mnl, labels, label_u, label_v):
          return process_edges(edges.tail, labels, mnl)
        else:
          if label_u > label_v:
            new_label = label_u
          else:
            new_label = label_v
          merged = replace_labels(labels, label_u, label_v, new_label)
          return process_edges(edges.tail, merged, mnl)

def has_crossing_link(mnl, labels, label_a, label_b):
  match mnl:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = mnl.head
      label_a_node = get_label(labels, a)
      label_b_node = get_label(labels, b)
      if label_a_node == label_a:
        if label_b_node == label_b:
          return 1
        else:
          return has_crossing_link(mnl.tail, labels, label_a, label_b)
      else:
        if label_a_node == label_b:
          if label_b_node == label_a:
            return 1
          else:
            return has_crossing_link(mnl.tail, labels, label_a, label_b)
        else:
          return has_crossing_link(mnl.tail, labels, label_a, label_b)

def replace_labels(labels, old_a, old_b, new_label):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      if labels.head == old_a:
        return List/Cons(new_label, replace_labels(labels.tail, old_a, old_b, new_label))
      else:
        if labels.head == old_b:
          return List/Cons(new_label, replace_labels(labels.tail, old_a, old_b, new_label))
        else:
          return List/Cons(labels.head, replace_labels(labels.tail, old_a, old_b, new_label))
