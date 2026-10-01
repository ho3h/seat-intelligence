def prog(x):
  (n, tau, mnl, cands, edges) = x
  labels = build_labels(0, n)
  all_cands = consolidate(cands, [])
  ordered = accepted_sorted(all_cands, tau, [])
  final_labels = process_pairs(ordered, mnl, labels)
  final_edges = rewrite_edges(edges, final_labels, [])
  return (final_labels, final_edges)

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

def add_candidate(cs, u, v, score):
  match cs:
    case List/Nil:
      return List/Cons((u, v, score), [])
    case List/Cons:
      (a, b, old_score) = cs.head
      if u == a:
        if v == b:
          if score > old_score:
            return List/Cons((u, v, score), cs.tail)
          else:
            return cs
        else:
          return List/Cons(cs.head, add_candidate(cs.tail, u, v, score))
      else:
        return List/Cons(cs.head, add_candidate(cs.tail, u, v, score))

def consolidate(cands, acc):
  match cands:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = cands.head
      updated = add_candidate(acc, u, v, score)
      return consolidate(cands.tail, updated)

def insert_candidate(xs, item):
  match xs:
    case List/Nil:
      return List/Cons(item, [])
    case List/Cons:
      (u, v, score) = item
      (a, b, old_score) = xs.head
      if score > old_score:
        return List/Cons(item, xs)
      else:
        if score == old_score:
          if u < a:
            return List/Cons(item, xs)
          else:
            if u == a:
              if v < b:
                return List/Cons(item, xs)
              else:
                return List/Cons(xs.head, insert_candidate(xs.tail, item))
            else:
              return List/Cons(xs.head, insert_candidate(xs.tail, item))
        else:
          return List/Cons(xs.head, insert_candidate(xs.tail, item))

def accepted_sorted(cands, tau, acc):
  match cands:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        updated = insert_candidate(acc, (u, v, score))
        return accepted_sorted(cands.tail, tau, updated)
      else:
        return accepted_sorted(cands.tail, tau, acc)

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

def insert_edge(edges, item):
  match edges:
    case List/Nil:
      return List/Cons(item, [])
    case List/Cons:
      (u, v) = item
      (a, b) = edges.head
      if u < a:
        return List/Cons(item, edges)
      else:
        if u == a:
          if v < b:
            return List/Cons(item, edges)
          else:
            if v == b:
              return edges
            else:
              return List/Cons(edges.head, insert_edge(edges.tail, item))
        else:
          return List/Cons(edges.head, insert_edge(edges.tail, item))

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
          item = (a, b)
        else:
          item = (b, a)
        updated = insert_edge(acc, item)
        return rewrite_edges(edges.tail, labels, updated)
