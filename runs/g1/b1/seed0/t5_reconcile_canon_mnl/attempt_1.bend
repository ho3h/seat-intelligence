def prog(x):
  (n, tau, mnl, cands) = x
  unique = dedup(cands, [])
  ordered = collect_accepted(unique, tau, [])
  labels = make_labels(0, n)
  return process_edges(ordered, labels, mnl)

def make_labels(i, n):
  if i >= n:
    return []
  else:
    return List/Cons(i, make_labels(i + 1, n))

def dedup(cands, acc):
  match cands:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = cands.head
      return dedup(cands.tail, upsert_edge(acc, u, v, score))

def upsert_edge(edges, u, v, score):
  match edges:
    case List/Nil:
      return List/Cons((u, v, score), [])
    case List/Cons:
      (eu, ev, old_score) = edges.head
      if eu == u:
        if ev == v:
          if score > old_score:
            return List/Cons((u, v, score), edges.tail)
          else:
            return edges
        else:
          return List/Cons(edges.head, upsert_edge(edges.tail, u, v, score))
      else:
        return List/Cons(edges.head, upsert_edge(edges.tail, u, v, score))

def collect_accepted(edges, tau, sorted):
  match edges:
    case List/Nil:
      return sorted
    case List/Cons:
      (u, v, score) = edges.head
      if score >= tau:
        return collect_accepted(edges.tail, tau, insert_sorted(edges.head, sorted))
      else:
        return collect_accepted(edges.tail, tau, sorted)

def insert_sorted(edge, sorted):
  match sorted:
    case List/Nil:
      return List/Cons(edge, [])
    case List/Cons:
      if edge_before(edge, sorted.head):
        return List/Cons(edge, sorted)
      else:
        return List/Cons(sorted.head, insert_sorted(edge, sorted.tail))

def edge_before(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if s1 > s2:
    return true
  else:
    if s1 < s2:
      return false
    else:
      if u1 < u2:
        return true
      else:
        if u1 > u2:
          return false
        else:
          return v1 < v2

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
      return false
    case List/Cons:
      (a, b) = mnl.head
      label_a_node = get_label(labels, a)
      label_b_node = get_label(labels, b)
      if label_a_node == label_a:
        if label_b_node == label_b:
          return true
        else:
          return has_crossing_link(mnl.tail, labels, label_a, label_b)
      else:
        if label_a_node == label_b:
          if label_b_node == label_a:
            return true
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
