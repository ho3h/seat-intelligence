def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  ids = make_ids(0, n)
  ordered = collect_ordered_candidates(cands, tau, [])
  final_ids = reconcile(ordered, ids, mnl)
  final_edges = rewrite_edges(edges, final_ids, [])
  counts = collect_counts(attrs, final_ids, [])
  winners = collect_winners(counts, [])
  props = props_from_winners(winners, [])
  return (final_ids, final_edges, props)

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

def collect_ordered_candidates(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        next = ordered_candidate_upsert(acc, u, v, score)
        return collect_ordered_candidates(xs.tail, tau, next)
      else:
        return collect_ordered_candidates(xs.tail, tau, acc)

def ordered_candidate_upsert(xs, u, v, score):
  match xs:
    case List/Nil:
      return List/Cons((u, v, score), [])
    case List/Cons:
      (a, b, old_score) = xs.head
      if u == a:
        if v == b:
          if score > old_score:
            rest = remove_candidate_pair(xs, u, v)
            return candidate_insert_sorted(rest, u, v, score)
          else:
            return xs
        else:
          rest = ordered_candidate_upsert(xs.tail, u, v, score)
          return List/Cons(xs.head, rest)
      else:
        rest = ordered_candidate_upsert(xs.tail, u, v, score)
        return List/Cons(xs.head, rest)

def remove_candidate_pair(xs, u, v):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b, score) = xs.head
      if u == a:
        if v == b:
          return remove_candidate_pair(xs.tail, u, v)
        else:
          return List/Cons(xs.head, remove_candidate_pair(xs.tail, u, v))
      else:
        return List/Cons(xs.head, remove_candidate_pair(xs.tail, u, v))

def candidate_insert_sorted(xs, u, v, score):
  match xs:
    case List/Nil:
      return List/Cons((u, v, score), [])
    case List/Cons:
      (a, b, old_score) = xs.head
      if score > old_score:
        return List/Cons((u, v, score), xs)
      else:
        if score == old_score:
          if u < a:
            return List/Cons((u, v, score), xs)
          else:
            if u == a:
              if v < b:
                return List/Cons((u, v, score), xs)
              else:
                rest = candidate_insert_sorted(xs.tail, u, v, score)
                return List/Cons(xs.head, rest)
            else:
              rest = candidate_insert_sorted(xs.tail, u, v, score)
              return List/Cons(xs.head, rest)
        else:
          rest = candidate_insert_sorted(xs.tail, u, v, score)
          return List/Cons(xs.head, rest)

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

def rewrite_edges(xs, labels, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = xs.head
      a = get_at(labels, u)
      b = get_at(labels, v)
      if a == b:
        return rewrite_edges(xs.tail, labels, acc)
      else:
        if a < b:
          next = edge_insert_sorted(acc, a, b)
          return rewrite_edges(xs.tail, labels, next)
        else:
          next = edge_insert_sorted(acc, b, a)
          return rewrite_edges(xs.tail, labels, next)

def edge_insert_sorted(xs, u, v):
  match xs:
    case List/Nil:
      return List/Cons((u, v), [])
    case List/Cons:
      (a, b) = xs.head
      if u == a:
        if v == b:
          return xs
        else:
          if v < b:
            return List/Cons((u, v), xs)
          else:
            rest = edge_insert_sorted(xs.tail, u, v)
            return List/Cons(xs.head, rest)
      else:
        if u < a:
          return List/Cons((u, v), xs)
        else:
          rest = edge_insert_sorted(xs.tail, u, v)
          return List/Cons(xs.head, rest)

def collect_counts(xs, labels, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, key, value) = xs.head
      cid = get_at(labels, node)
      next = count_upsert(acc, cid, key, value)
      return collect_counts(xs.tail, labels, next)

def count_upsert(xs, cid, key, value):
  match xs:
    case List/Nil:
      return List/Cons((cid, key, value, 1), [])
    case List/Cons:
      (old_cid, old_key, old_value, count) = xs.head
      if cid == old_cid:
        if key == old_key:
          if value == old_value:
            return List/Cons((cid, key, value, count + 1), xs.tail)
          else:
            rest = count_upsert(xs.tail, cid, key, value)
            return List/Cons(xs.head, rest)
        else:
          rest = count_upsert(xs.tail, cid, key, value)
          return List/Cons(xs.head, rest)
      else:
        rest = count_upsert(xs.tail, cid, key, value)
        return List/Cons(xs.head, rest)

def collect_winners(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (cid, key, value, count) = xs.head
      next = winner_upsert(acc, cid, key, value, count)
      return collect_winners(xs.tail, next)

def winner_upsert(xs, cid, key, value, count):
  match xs:
    case List/Nil:
      return List/Cons((cid, key, value, count), [])
    case List/Cons:
      (old_cid, old_key, old_value, old_count) = xs.head
      if cid == old_cid:
        if key == old_key:
          if count > old_count:
            return List/Cons((cid, key, value, count), xs.tail)
          else:
            if count == old_count:
              if value < old_value:
                return List/Cons((cid, key, value, count), xs.tail)
              else:
                return xs
            else:
              return xs
        else:
          rest = winner_upsert(xs.tail, cid, key, value, count)
          return List/Cons(xs.head, rest)
      else:
        rest = winner_upsert(xs.tail, cid, key, value, count)
        return List/Cons(xs.head, rest)

def props_from_winners(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (cid, key, value, count) = xs.head
      next = prop_insert_sorted(acc, cid, key, value)
      return props_from_winners(xs.tail, next)

def prop_insert_sorted(xs, cid, key, value):
  match xs:
    case List/Nil:
      return List/Cons((cid, key, value), [])
    case List/Cons:
      (old_cid, old_key, old_value) = xs.head
      if cid == old_cid:
        if key == old_key:
          return xs
        else:
          if key < old_key:
            return List/Cons((cid, key, value), xs)
          else:
            rest = prop_insert_sorted(xs.tail, cid, key, value)
            return List/Cons(xs.head, rest)
      else:
        if cid < old_cid:
          return List/Cons((cid, key, value), xs)
        else:
          rest = prop_insert_sorted(xs.tail, cid, key, value)
          return List/Cons(xs.head, rest)
