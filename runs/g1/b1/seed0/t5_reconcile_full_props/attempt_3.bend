def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  ids = make_ids(0, n)

  sorted_cands = sort_cands(cands, 0)
  distinct_cands = unique_cands(sorted_cands)
  accepted = filter_accepted(distinct_cands, tau)
  ordered = sort_cands(accepted, 1)

  final_ids = reconcile(ordered, ids, mnl)

  rewritten = map_edges(edges, final_ids)
  sorted_edges = sort_edges(rewritten)
  final_edges = unique_edges(sorted_edges)

  prop_rows = map_attrs(attrs, final_ids)
  sorted_props = sort_props(prop_rows)
  counted_props = count_prop_runs(sorted_props)
  final_props = choose_props(counted_props)

  return (final_ids, final_edges, final_props)

def make_ids(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_ids(i + 1, n))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def split_cands(xs, left, right, turn):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_cands(xs.tail, List/Cons(xs.head, left), right, 1)
      else:
        return split_cands(xs.tail, left, List/Cons(xs.head, right), 0)

def cand_before(x, y, mode):
  (u, v, score) = x
  (a, b, old_score) = y
  if mode == 0:
    if u < a:
      return 1
    else:
      if u == a:
        if v < b:
          return 1
        else:
          if v == b:
            if score > old_score:
              return 1
            else:
              return 0
          else:
            return 0
      else:
        return 0
  else:
    if score > old_score:
      return 1
    else:
      if score == old_score:
        if u < a:
          return 1
        else:
          if u == a:
            if v < b:
              return 1
            else:
              return 0
          else:
            return 0
      else:
        return 0

def merge_cands(xs, ys, mode):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if cand_before(xs.head, ys.head, mode) == 1:
            return List/Cons(xs.head, merge_cands(xs.tail, ys, mode))
          else:
            return List/Cons(ys.head, merge_cands(xs, ys.tail, mode))

def sort_cands(xs, mode):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_cands(xs, [], [], 0)
          sorted_left = sort_cands(left, mode)
          sorted_right = sort_cands(right, mode)
          return merge_cands(sorted_left, sorted_right, mode)

def drop_cand_pair(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b, score) = xs.head
      if u == a:
        if v == b:
          return drop_cand_pair(xs.tail, u, v)
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
      return List/Cons(xs.head, unique_cands(drop_cand_pair(xs.tail, u, v)))

def filter_accepted(xs, tau):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        return List/Cons(xs.head, filter_accepted(xs.tail, tau))
      else:
        return filter_accepted(xs.tail, tau)

def reconcile(xs, labels, mnl):
  match xs:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = xs.head
      a_id = get_at(labels, u)
      b_id = get_at(labels, v)
      if a_id == b_id:
        return reconcile(xs.tail, labels, mnl)
      else:
        blocked = has_conflict(mnl, labels, a_id, b_id)
        if blocked == 1:
          return reconcile(xs.tail, labels, mnl)
        else:
          if a_id > b_id:
            merged = merge_labels(labels, a_id, b_id, a_id)
            return reconcile(xs.tail, merged, mnl)
          else:
            merged = merge_labels(labels, a_id, b_id, b_id)
            return reconcile(xs.tail, merged, mnl)

def has_conflict(xs, labels, a_id, b_id):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = xs.head
      left = get_at(labels, a)
      right = get_at(labels, b)
      if left == a_id:
        if right == b_id:
          return 1
        else:
          return has_conflict(xs.tail, labels, a_id, b_id)
      else:
        if left == b_id:
          if right == a_id:
            return 1
          else:
            return has_conflict(xs.tail, labels, a_id, b_id)
        else:
          return has_conflict(xs.tail, labels, a_id, b_id)

def merge_labels(xs, a_id, b_id, new_id):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == a_id:
        return List/Cons(new_id, merge_labels(xs.tail, a_id, b_id, new_id))
      else:
        if xs.head == b_id:
          return List/Cons(new_id, merge_labels(xs.tail, a_id, b_id, new_id))
        else:
          return List/Cons(xs.head, merge_labels(xs.tail, a_id, b_id, new_id))

def map_edges(xs, labels):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = xs.head
      a = get_at(labels, u)
      b = get_at(labels, v)
      if a == b:
        return map_edges(xs.tail, labels)
      else:
        if a < b:
          return List/Cons((a, b), map_edges(xs.tail, labels))
        else:
          return List/Cons((b, a), map_edges(xs.tail, labels))

def split_edges(xs, left, right, turn):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_edges(xs.tail, List/Cons(xs.head, left), right, 1)
      else:
        return split_edges(xs.tail, left, List/Cons(xs.head, right), 0)

def edge_before(x, y):
  (u, v) = x
  (a, b) = y
  if u < a:
    return 1
  else:
    if u == a:
      if v < b:
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
          (left, right) = split_edges(xs, [], [], 0)
          sorted_left = sort_edges(left)
          sorted_right = sort_edges(right)
          return merge_edges(sorted_left, sorted_right)

def drop_edge_pair(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = xs.head
      if u == a:
        if v == b:
          return drop_edge_pair(xs.tail, u, v)
        else:
          return xs
      else:
        return xs

def unique_edges(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = xs.head
      return List/Cons(xs.head, unique_edges(drop_edge_pair(xs.tail, u, v)))

def map_attrs(xs, labels):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = xs.head
      cid = get_at(labels, node)
      return List/Cons((cid, key, value), map_attrs(xs.tail, labels))

def split_props(xs, left, right, turn):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_props(xs.tail, List/Cons(xs.head, left), right, 1)
      else:
        return split_props(xs.tail, left, List/Cons(xs.head, right), 0)

def prop_before(x, y):
  (cid, key, value) = x
  (old_cid, old_key, old_value) = y
  if cid < old_cid:
    return 1
  else:
    if cid == old_cid:
      if key < old_key:
        return 1
      else:
        if key == old_key:
          if value < old_value:
            return 1
          else:
            return 0
        else:
          return 0
    else:
      return 0

def merge_props(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if prop_before(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge_props(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_props(xs, ys.tail))

def sort_props(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_props(xs, [], [], 0)
          sorted_left = sort_props(left)
          sorted_right = sort_props(right)
          return merge_props(sorted_left, sorted_right)

def consume_same_prop(xs, cid, key, value, count):
  match xs:
    case List/Nil:
      return (count, [])
    case List/Cons:
      (old_cid, old_key, old_value) = xs.head
      if cid == old_cid:
        if key == old_key:
          if value == old_value:
            return consume_same_prop(xs.tail, cid, key, value, count + 1)
          else:
            return (count, xs)
        else:
          return (count, xs)
      else:
        return (count, xs)

def count_prop_runs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (cid, key, value) = xs.head
      (count, rest) = consume_same_prop(xs.tail, cid, key, value, 1)
      return List/Cons((cid, key, value, count), count_prop_runs(rest))

def choose_best_prop(xs, cid, key, value, count):
  match xs:
    case List/Nil:
      return ((cid, key, value, count), [])
    case List/Cons:
      (next_cid, next_key, next_value, next_count) = xs.head
      if cid == next_cid:
        if key == next_key:
          if next_count > count:
            return choose_best_prop(xs.tail, cid, key, next_value, next_count)
          else:
            if next_count == count:
              if next_value < value:
                return choose_best_prop(xs.tail, cid, key, next_value, next_count)
              else:
                return choose_best_prop(xs.tail, cid, key, value, count)
            else:
              return choose_best_prop(xs.tail, cid, key, value, count)
        else:
          return ((cid, key, value, count), xs)
      else:
        return ((cid, key, value, count), xs)

def choose_props(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (cid, key, value, count) = xs.head
      (best, rest) = choose_best_prop(xs.tail, cid, key, value, count)
      (best_cid, best_key, best_value, best_count) = best
      return List/Cons((best_cid, best_key, best_value), choose_props(rest))
