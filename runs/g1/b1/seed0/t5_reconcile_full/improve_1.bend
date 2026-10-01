def prog(x):
  (n, tau, mnl, cands, edges) = x
  labels = build_labels(0, n)
  pair_sorted = sort_candidates(cands)
  accepted_rev = collect_candidates(pair_sorted, tau, 0, 0, 0, 0, [])
  accepted = reverse_candidates(accepted_rev)
  ordered = sort_by_priority(accepted)
  final_labels = process_pairs(ordered, mnl, labels)
  raw_edges = rewrite_edges(edges, final_labels, [])
  sorted_edges = sort_edges(raw_edges)
  distinct_rev = unique_edges(sorted_edges, [])
  return (final_labels, reverse_edges(distinct_rev))

def build_labels(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, build_labels(i + 1, n))

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def split_candidates(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_candidates(xs.tail)
      return (List/Cons(xs.head, right), left)

def candidate_pair_before(a, b):
  (u, v, score) = a
  (x, y, other_score) = b
  if u < x:
    return 1
  else:
    if u == x:
      if v <= y:
        return 1
      else:
        return 0
    else:
      return 0

def merge_candidates(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if candidate_pair_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_candidates(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_candidates(xs, ys.tail))

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_candidates(xs)
          return merge_candidates(sort_candidates(left), sort_candidates(right))

def flush_candidate(acc, tau, have, u, v, score):
  if have == 1:
    if score >= tau:
      return List/Cons((u, v, score), acc)
    else:
      return acc
  else:
    return acc

def collect_candidates(xs, tau, have, u, v, best, acc):
  match xs:
    case List/Nil:
      return flush_candidate(acc, tau, have, u, v, best)
    case List/Cons:
      (a, b, score) = xs.head
      if have == 0:
        return collect_candidates(xs.tail, tau, 1, a, b, score, acc)
      else:
        if a == u:
          if b == v:
            if score > best:
              return collect_candidates(xs.tail, tau, 1, u, v, score, acc)
            else:
              return collect_candidates(xs.tail, tau, 1, u, v, best, acc)
          else:
            updated = flush_candidate(acc, tau, have, u, v, best)
            return collect_candidates(xs.tail, tau, 1, a, b, score, updated)
        else:
          updated = flush_candidate(acc, tau, have, u, v, best)
          return collect_candidates(xs.tail, tau, 1, a, b, score, updated)

def reverse_candidates(xs):
  return reverse_candidates_go(xs, [])

def reverse_candidates_go(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_candidates_go(xs.tail, List/Cons(xs.head, acc))

def priority_before(a, b):
  (u, v, score) = a
  (x, y, other_score) = b
  if score > other_score:
    return 1
  else:
    if score == other_score:
      if u < x:
        return 1
      else:
        if u == x:
          if v <= y:
            return 1
          else:
            return 0
        else:
          return 0
    else:
      return 0

def split_priority(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_priority(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_priority(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if priority_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_priority(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_priority(xs, ys.tail))

def sort_by_priority(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_priority(xs)
          return merge_priority(sort_by_priority(left), sort_by_priority(right))

def has_conflict(mnl, labels, ra, rb):
  match mnl:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = mnl.head
      la = at(labels, a)
      lb = at(labels, b)
      if la == ra:
        if lb == rb:
          return 1
        else:
          return has_conflict(mnl.tail, labels, ra, rb)
      else:
        if la == rb:
          if lb == ra:
            return 1
          else:
            return has_conflict(mnl.tail, labels, ra, rb)
        else:
          return has_conflict(mnl.tail, labels, ra, rb)

def merge_labels(labels, ra, rb):
  if ra > rb:
    target = ra
  else:
    target = rb
  return replace_labels(labels, ra, rb, target)

def replace_labels(labels, ra, rb, target):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      if labels.head == ra:
        return List/Cons(target, replace_labels(labels.tail, ra, rb, target))
      else:
        if labels.head == rb:
          return List/Cons(target, replace_labels(labels.tail, ra, rb, target))
        else:
          return List/Cons(labels.head, replace_labels(labels.tail, ra, rb, target))

def process_pairs(pairs, mnl, labels):
  match pairs:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = pairs.head
      ra = at(labels, u)
      rb = at(labels, v)
      if ra == rb:
        return process_pairs(pairs.tail, mnl, labels)
      else:
        conflict = has_conflict(mnl, labels, ra, rb)
        if conflict == 1:
          return process_pairs(pairs.tail, mnl, labels)
        else:
          updated = merge_labels(labels, ra, rb)
          return process_pairs(pairs.tail, mnl, updated)

def split_edges(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_edges(xs.tail)
      return (List/Cons(xs.head, right), left)

def edge_before(a, b):
  (u, v) = a
  (x, y) = b
  if u < x:
    return 1
  else:
    if u == x:
      if v <= y:
        return 1
      else:
        return 0
    else:
      return 0

def merge_edges(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if edge_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_edges(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_edges(xs, ys.tail))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_edges(xs)
          return merge_edges(sort_edges(left), sort_edges(right))

def rewrite_edges(edges, labels, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      a = at(labels, u)
      b = at(labels, v)
      if a == b:
        return rewrite_edges(edges.tail, labels, acc)
      else:
        if a < b:
          return rewrite_edges(edges.tail, labels, List/Cons((a, b), acc))
        else:
          return rewrite_edges(edges.tail, labels, List/Cons((b, a), acc))

def unique_edges(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return List/Cons(xs.head, acc)
        case List/Cons:
          if xs.head == xs.tail.head:
            return unique_edges(xs.tail, acc)
          else:
            return unique_edges(xs.tail, List/Cons(xs.head, acc))

def reverse_edges(xs):
  return reverse_edges_go(xs, [])

def reverse_edges_go(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_edges_go(xs.tail, List/Cons(xs.head, acc))
