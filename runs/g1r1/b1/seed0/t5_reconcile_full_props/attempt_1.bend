def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  labels = make_labels(0, n)
  unique_cands = dedup_cands(cands, [])
  ordered_cands = prepare_cands(unique_cands, tau, [])
  final_labels = process_cands(ordered_cands, labels, mnl)
  final_edges = rewrite_edges(edges, final_labels, [])
  rev_props = props_nodes(0, n, final_labels, attrs, [])
  props = reverse(rev_props)
  return (final_labels, final_edges, props)

def make_labels(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_labels(i + 1, n))

def nth(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return nth(xs.tail, i - 1)

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def dedup_cands(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      acc2 = add_candidate(acc, xs.head)
      return dedup_cands(xs.tail, acc2)

def add_candidate(xs, cand):
  (u, v, score) = cand
  match xs:
    case List/Nil:
      return List/Cons(cand, [])
    case List/Cons:
      (a, b, old_score) = xs.head
      if u == a:
        if v == b:
          if score > old_score:
            return List/Cons((u, v, score), xs.tail)
          else:
            return List/Cons(xs.head, xs.tail)
        else:
          return List/Cons(xs.head, add_candidate(xs.tail, cand))
      else:
        return List/Cons(xs.head, add_candidate(xs.tail, cand))

def prepare_cands(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        acc2 = insert_ranked(acc, xs.head)
        return prepare_cands(xs.tail, tau, acc2)
      else:
        return prepare_cands(xs.tail, tau, acc)

def cand_before(a, b):
  (u, v, score) = a
  (bu, bv, bscore) = b
  if score > bscore:
    return 1
  else:
    if score < bscore:
      return 0
    else:
      if u < bu:
        return 1
      else:
        if u > bu:
          return 0
        else:
          if v < bv:
            return 1
          else:
            return 0

def insert_ranked(xs, cand):
  match xs:
    case List/Nil:
      return List/Cons(cand, [])
    case List/Cons:
      if cand_before(cand, xs.head) == 1:
        return List/Cons(cand, xs)
      else:
        return List/Cons(xs.head, insert_ranked(xs.tail, cand))

def process_cands(xs, labels, mnl):
  match xs:
    case List/Nil:
      return labels
    case List/Cons:
      labels2 = try_merge(xs.head, labels, mnl)
      return process_cands(xs.tail, labels2, mnl)

def try_merge(cand, labels, mnl):
  (u, v, score) = cand
  ca = nth(labels, u)
  cb = nth(labels, v)
  if ca == cb:
    return labels
  else:
    if has_crossing_mnl(mnl, labels, ca, cb) == 1:
      return labels
    else:
      if ca > cb:
        new_id = ca
      else:
        new_id = cb
      return replace_merge(labels, ca, cb, new_id)

def has_crossing_mnl(xs, labels, ca, cb):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = xs.head
      la = nth(labels, a)
      lb = nth(labels, b)
      if la == ca:
        if lb == cb:
          return 1
        else:
          return has_crossing_mnl(xs.tail, labels, ca, cb)
      else:
        if la == cb:
          if lb == ca:
            return 1
          else:
            return has_crossing_mnl(xs.tail, labels, ca, cb)
        else:
          return has_crossing_mnl(xs.tail, labels, ca, cb)

def replace_merge(xs, ca, cb, new_id):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == ca:
        return List/Cons(new_id, replace_merge(xs.tail, ca, cb, new_id))
      else:
        if xs.head == cb:
          return List/Cons(new_id, replace_merge(xs.tail, ca, cb, new_id))
        else:
          return List/Cons(xs.head, replace_merge(xs.tail, ca, cb, new_id))

def rewrite_edges(xs, labels, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = xs.head
      a = nth(labels, u)
      b = nth(labels, v)
      if a == b:
        return rewrite_edges(xs.tail, labels, acc)
      else:
        if a < b:
          acc2 = insert_edge(acc, (a, b))
          return rewrite_edges(xs.tail, labels, acc2)
        else:
          acc2 = insert_edge(acc, (b, a))
          return rewrite_edges(xs.tail, labels, acc2)

def insert_edge(xs, pair):
  (u, v) = pair
  match xs:
    case List/Nil:
      return List/Cons(pair, [])
    case List/Cons:
      (a, b) = xs.head
      if u < a:
        return List/Cons(pair, xs)
      else:
        if u == a:
          if v < b:
            return List/Cons(pair, xs)
          else:
            if v == b:
              return xs
            else:
              return List/Cons(xs.head, insert_edge(xs.tail, pair))
        else:
          return List/Cons(xs.head, insert_edge(xs.tail, pair))

def attr_frequency(attrs, labels, cid, key, value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (node, attr_key, attr_value) = attrs.head
      if attr_key == key:
        if attr_value == value:
          if nth(labels, node) == cid:
            return 1 + attr_frequency(attrs.tail, labels, cid, key, value)
          else:
            return attr_frequency(attrs.tail, labels, cid, key, value)
        else:
          return attr_frequency(attrs.tail, labels, cid, key, value)
      else:
        return attr_frequency(attrs.tail, labels, cid, key, value)

def best_attr(attrs, labels, cid, key, found, best_value, best_count):
  match attrs:
    case List/Nil:
      return (found, best_value)
    case List/Cons:
      (node, attr_key, value) = attrs.head
      if attr_key == key:
        if nth(labels, node) == cid:
          count = attr_frequency(attrs, labels, cid, key, value)
          if found == 0:
            return best_attr(attrs.tail, labels, cid, key, 1, value, count)
          else:
            if count > best_count:
              return best_attr(attrs.tail, labels, cid, key, 1, value, count)
            else:
              if count == best_count:
                if value < best_value:
                  return best_attr(attrs.tail, labels, cid, key, 1, value, count)
                else:
                  return best_attr(attrs.tail, labels, cid, key, found, best_value, best_count)
              else:
                return best_attr(attrs.tail, labels, cid, key, found, best_value, best_count)
        else:
          return best_attr(attrs.tail, labels, cid, key, found, best_value, best_count)
      else:
        return best_attr(attrs.tail, labels, cid, key, found, best_value, best_count)

def props_keys(cid, key, labels, attrs, acc):
  if key == 4:
    return acc
  else:
    (found, value) = best_attr(attrs, labels, cid, key, 0, 0, 0)
    if found == 1:
      acc2 = List/Cons((cid, key, value), acc)
      return props_keys(cid, key + 1, labels, attrs, acc2)
    else:
      return props_keys(cid, key + 1, labels, attrs, acc)

def props_nodes(i, n, labels, attrs, acc):
  if i == n:
    return acc
  else:
    cid = nth(labels, i)
    if cid == i:
      acc2 = props_keys(cid, 0, labels, attrs, acc)
      return props_nodes(i + 1, n, labels, attrs, acc2)
    else:
      return props_nodes(i + 1, n, labels, attrs, acc)
