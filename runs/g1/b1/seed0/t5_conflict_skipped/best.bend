def prog(x):
  (n, cap, mnl, cands) = x
  labels = make_labels(0, n)
  return process(cands, labels, mnl, cap, [])

def make_labels(i, n):
  if i < n:
    return List/Cons(i, make_labels(i + 1, n))
  else:
    return []

def candidate_precedes(a, b):
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

def pick_candidate(xs):
  match xs:
    case List/Nil:
      return ((0, 0, 0), [])
    case List/Cons:
      return choose_candidate(xs.tail, xs.head)

def choose_candidate(xs, best):
  match xs:
    case List/Nil:
      return (best, [])
    case List/Cons:
      if candidate_precedes(xs.head, best) == 1:
        (found, rest) = choose_candidate(xs.tail, xs.head)
        return (found, List/Cons(best, rest))
      else:
        (found, rest) = choose_candidate(xs.tail, best)
        return (found, List/Cons(xs.head, rest))

def label_at(labels, i):
  match labels:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return labels.head
      else:
        return label_at(labels.tail, i - 1)

def count_label(labels, target):
  match labels:
    case List/Nil:
      return 0
    case List/Cons:
      rest = count_label(labels.tail, target)
      if labels.head == target:
        return rest + 1
      else:
        return rest

def has_conflict(mnl, labels, la, lb):
  match mnl:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = mnl.head
      label_a = label_at(labels, a)
      label_b = label_at(labels, b)
      if label_a == la:
        if label_b == lb:
          return 1
        else:
          return has_conflict(mnl.tail, labels, la, lb)
      else:
        if label_a == lb:
          if label_b == la:
            return 1
          else:
            return has_conflict(mnl.tail, labels, la, lb)
        else:
          return has_conflict(mnl.tail, labels, la, lb)

def replace_label(labels, old_label, new_label):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = replace_label(labels.tail, old_label, new_label)
      if labels.head == old_label:
        return List/Cons(new_label, tail)
      else:
        return List/Cons(labels.head, tail)

def reverse_pairs(xs):
  return reverse_pairs_acc(xs, [])

def reverse_pairs_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_pairs_acc(xs.tail, List/Cons(xs.head, acc))

def process(cands, labels, mnl, cap, skipped_rev):
  match cands:
    case List/Nil:
      return reverse_pairs(skipped_rev)
    case List/Cons:
      (cand, remaining) = pick_candidate(cands)
      (u, v, score) = cand
      la = label_at(labels, u)
      lb = label_at(labels, v)
      if la == lb:
        return process(remaining, labels, mnl, cap, skipped_rev)
      else:
        size_a = count_label(labels, la)
        size_b = count_label(labels, lb)
        if size_a + size_b > cap:
          return process(remaining, labels, mnl, cap, List/Cons((u, v), skipped_rev))
        else:
          if has_conflict(mnl, labels, la, lb) == 1:
            return process(remaining, labels, mnl, cap, List/Cons((u, v), skipped_rev))
          else:
            merged = replace_label(labels, lb, la)
            return process(remaining, merged, mnl, cap, skipped_rev)
