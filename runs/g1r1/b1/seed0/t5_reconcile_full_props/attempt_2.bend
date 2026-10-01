def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  labels = make_labels(0, n)
  unique_cands = dedup_cands(cands, [])
  ordered_cands = prepare_cands(unique_cands, tau, [])
  final_labels = process_cands(ordered_cands, labels, mnl)
  final_edges = rewrite_edges(edges, final_labels, [])
  prop_records = make_prop_records(attrs, final_labels, [])
  props = property_output(prop_records)
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

def make_prop_records(attrs, labels, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, key, value) = attrs.head
      cid = nth(labels, node)
      acc2 = insert_prop(acc, (cid, key, value))
      return make_prop_records(attrs.tail, labels, acc2)

def prop_before(a, b):
  (cid, key, value) = a
  (bcid, bkey, bvalue) = b
  if cid < bcid:
    return 1
  else:
    if cid > bcid:
      return 0
    else:
      if key < bkey:
        return 1
      else:
        if key > bkey:
          return 0
        else:
          if value < bvalue:
            return 1
          else:
            return 0

def insert_prop(xs, record):
  match xs:
    case List/Nil:
      return List/Cons(record, [])
    case List/Cons:
      if prop_before(record, xs.head) == 1:
        return List/Cons(record, xs)
      else:
        return List/Cons(xs.head, insert_prop(xs.tail, record))

def consume_prop_value(xs, cid, key, value, count):
  match xs:
    case List/Nil:
      return (xs, count)
    case List/Cons:
      (next_cid, next_key, next_value) = xs.head
      if next_cid == cid:
        if next_key == key:
          if next_value == value:
            return consume_prop_value(xs.tail, cid, key, value, count + 1)
          else:
            return (xs, count)
        else:
          return (xs, count)
      else:
        return (xs, count)

def best_prop(xs, cid, key, best_value, best_count):
  match xs:
    case List/Nil:
      return (best_value, best_count, xs)
    case List/Cons:
      (next_cid, next_key, value) = xs.head
      if next_cid == cid:
        if next_key == key:
          (rest, count) = consume_prop_value(xs.tail, cid, key, value, 1)
          if count > best_count:
            return best_prop(rest, cid, key, value, count)
          else:
            return best_prop(rest, cid, key, best_value, best_count)
        else:
          return (best_value, best_count, xs)
      else:
        return (best_value, best_count, xs)

def property_output(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (cid, key, value) = xs.head
      (rest, count) = consume_prop_value(xs.tail, cid, key, value, 1)
      (best_value, best_count, after) = best_prop(rest, cid, key, value, count)
      return List/Cons((cid, key, best_value), property_output(after))
