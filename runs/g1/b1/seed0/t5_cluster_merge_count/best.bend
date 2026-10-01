def prog(x):
  (n, tau, cands) = x
  accepted = filter_candidates(cands, tau)
  ordered = merge_sort(accepted)
  labels = make_labels(0, n)
  return merge_edges(ordered, labels, 0)

def filter_candidates(xs, tau):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v, score) = xs.head
      rest = filter_candidates(xs.tail, tau)
      if score >= tau:
        return List/Cons(xs.head, rest)
      else:
        return rest

def merge_sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternate(xs, 0)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_sorted(sorted_left, sorted_right)

def split_alternate(xs, turn):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (left, right) = split_alternate(xs.tail, 1 - turn)
      if turn == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def merge_sorted(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if comes_before(left.head, right.head) == 1:
            rest = merge_sorted(left.tail, right)
            return List/Cons(left.head, rest)
          else:
            rest = merge_sorted(left, right.tail)
            return List/Cons(right.head, rest)

def comes_before(a, b):
  (au, av, ascore) = a
  (bu, bv, bscore) = b
  if ascore > bscore:
    return 1
  else:
    if ascore < bscore:
      return 0
    else:
      if au < bu:
        return 1
      else:
        if au > bu:
          return 0
        else:
          if av < bv:
            return 1
          else:
            return 0

def make_labels(i, n):
  if i == n:
    return List/Nil
  else:
    rest = make_labels(i + 1, n)
    return List/Cons(i, rest)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def replace_label(xs, old_label, new_label):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = replace_label(xs.tail, old_label, new_label)
      if xs.head == old_label:
        return List/Cons(new_label, rest)
      else:
        return List/Cons(xs.head, rest)

def merge_edges(edges, labels, count):
  match edges:
    case List/Nil:
      return count
    case List/Cons:
      (u, v, score) = edges.head
      label_u = get_at(labels, u)
      label_v = get_at(labels, v)
      if label_u == label_v:
        return merge_edges(edges.tail, labels, count)
      else:
        next_labels = replace_label(labels, label_v, label_u)
        return merge_edges(edges.tail, next_labels, count + 1)
