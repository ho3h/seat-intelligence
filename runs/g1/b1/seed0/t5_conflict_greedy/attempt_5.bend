def prog(x):
  (n, mnl, cands) = x
  labels = make_range(0, n)
  ordered = sort_cands(cands)
  labels = process(ordered, labels, mnl)
  return make_output(labels, labels)

def make_range(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_range(i + 1, n))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def replace_value(xs, old, new):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, replace_value(xs.tail, old, new))
      else:
        return List/Cons(xs.head, replace_value(xs.tail, old, new))

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, []), [])
        case List/Cons:
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def before(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
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
          if v1 < v2:
            return 1
          else:
            return 0

def merge_cands(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_cands(a.tail, b))
          else:
            return List/Cons(b.head, merge_cands(a, b.tail))

def sort_cands(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort_cands(left)
          sorted_right = sort_cands(right)
          return merge_cands(sorted_left, sorted_right)

def has_conflict(edges, labels, rep_a, rep_b):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = edges.head
      label_a = get_at(labels, a)
      label_b = get_at(labels, b)
      if label_a == rep_a:
        if label_b == rep_b:
          return 1
        else:
          return has_conflict(edges.tail, labels, rep_a, rep_b)
      else:
        if label_a == rep_b:
          if label_b == rep_a:
            return 1
          else:
            return has_conflict(edges.tail, labels, rep_a, rep_b)
        else:
          return has_conflict(edges.tail, labels, rep_a, rep_b)

def process(cands, labels, mnl):
  match cands:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = cands.head
      rep_u = get_at(labels, u)
      rep_v = get_at(labels, v)
      if rep_u == rep_v:
        return process(cands.tail, labels, mnl)
      else:
        conflict = has_conflict(mnl, labels, rep_u, rep_v)
        if conflict == 1:
          return process(cands.tail, labels, mnl)
        else:
          new_labels = replace_value(labels, rep_v, rep_u)
          return process(cands.tail, new_labels, mnl)

def max_in_cluster(labels, rep, idx, best):
  match labels:
    case List/Nil:
      return best
    case List/Cons:
      if labels.head == rep:
        if idx > best:
          return max_in_cluster(labels.tail, rep, idx + 1, idx)
        else:
          return max_in_cluster(labels.tail, rep, idx + 1, best)
      else:
        return max_in_cluster(labels.tail, rep, idx + 1, best)

def make_output(labels, all_labels):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      largest = max_in_cluster(all_labels, labels.head, 0, 0)
      return List/Cons(largest, make_output(labels.tail, all_labels))
