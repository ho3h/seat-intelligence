def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  labels = make_labels(0, n)
  pair_sorted = sort_cands_pair(cands)
  unique = unique_cands(pair_sorted)
  accepted = filter_cands(unique, tau, [])
  ranked = sort_cands_rank(accepted)
  final_labels = process_cands(ranked, labels, mnl)
  edge_list = collect_edges(edges, final_labels, [])
  sorted_edges = sort_edges(edge_list)
  final_edges = unique_edges(sorted_edges)
  prop_list = collect_props(attrs, final_labels, [])
  sorted_props = sort_props(prop_list)
  props = property_output(sorted_props)
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

def split_cands(xs, flag, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if flag == 0:
        return split_cands(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_cands(xs.tail, 0, left, List/Cons(xs.head, right))

def cand_pair_before(a, b):
  (u, v, score) = a
  (bu, bv, bscore) = b
  if u < bu:
    return 1
  else:
    if u > bu:
      return 0
    else:
      if v < bv:
        return 1
      else:
        if v > bv:
          return 0
        else:
          if score > bscore:
            return 1
          else:
            return 0

def merge_cands_pair(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if cand_pair_before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_cands_pair(a.tail, b))
          else:
            return List/Cons(b.head, merge_cands_pair(a, b.tail))

def sort_cands_pair(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_cands(xs, 0, [], [])
          return merge_cands_pair(sort_cands_pair(left), sort_cands_pair(right))

def skip_same_cand(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b, score) = xs.head
      if a == u:
        if b == v:
          return skip_same_cand(xs.tail, u, v)
        else:
          return xs
      else:
        return xs

def unique_cands(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      rest = skip_same_cand(xs.tail, u, v)
      return List/Cons(xs.head, unique_cands(rest))

def filter_cands(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        return filter_cands(xs.tail, tau, List/Cons(xs.head, acc))
      else:
        return filter_cands(xs.tail, tau, acc)

def split_ranked(xs, flag, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if flag == 0:
        return split_ranked(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_ranked(xs.tail, 0, left, List/Cons(xs.head, right))

def cand_rank_before(a, b):
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

def merge_cands_rank(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if cand_rank_before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_cands_rank(a.tail, b))
          else:
            return List/Cons(b.head, merge_cands_rank(a, b.tail))

def sort_cands_rank(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_ranked(xs, 0, [], [])
          return merge_cands_rank(sort_cands_rank(left), sort_cands_rank(right))

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

def collect_edges(xs, labels, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = xs.head
      a = nth(labels, u)
      b = nth(labels, v)
      if a == b:
        return collect_edges(xs.tail, labels, acc)
      else:
        if a < b:
          return collect_edges(xs.tail, labels, List/Cons((a, b), acc))
        else:
          return collect_edges(xs.tail, labels, List/Cons((b, a), acc))

def split_edges(xs, flag, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if flag == 0:
        return split_edges(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_edges(xs.tail, 0, left, List/Cons(xs.head, right))

def edge_before(a, b):
  (u, v) = a
  (bu, bv) = b
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

def merge_edges(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if edge_before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_edges(a.tail, b))
          else:
            return List/Cons(b.head, merge_edges(a, b.tail))

def sort_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_edges(xs, 0, [], [])
          return merge_edges(sort_edges(left), sort_edges(right))

def skip_same_edge(xs, pair):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == pair:
        return skip_same_edge(xs.tail, pair)
      else:
        return xs

def unique_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = skip_same_edge(xs.tail, xs.head)
      return List/Cons(xs.head, unique_edges(rest))

def collect_props(xs, labels, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, key, value) = xs.head
      cid = nth(labels, node)
      return collect_props(xs.tail, labels, List/Cons((cid, key, value), acc))

def split_props(xs, flag, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if flag == 0:
        return split_props(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_props(xs.tail, 0, left, List/Cons(xs.head, right))

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

def merge_props(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if prop_before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_props(a.tail, b))
          else:
            return List/Cons(b.head, merge_props(a, b.tail))

def sort_props(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_props(xs, 0, [], [])
          return merge_props(sort_props(left), sort_props(right))

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
