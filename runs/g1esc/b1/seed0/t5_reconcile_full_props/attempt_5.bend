def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def reverse_list(xs):
  return reverse_acc(xs, List/Nil)

def range(n, acc):
  if n == 0:
    return acc
  else:
    return range(n - 1, List/Cons(n - 1, acc))

def repeat(val, count):
  if count == 0:
    return List/Nil
  else:
    return List/Cons(val, repeat(val, count - 1))

def list_get(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_get(xs.tail, i - 1)

def list_set(xs, i, val):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(val, xs.tail)
      else:
        return List/Cons(xs.head, list_set(xs.tail, i - 1, val))

def replace_all(xs, old, new):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, replace_all(xs.tail, old, new))
      else:
        return List/Cons(xs.head, replace_all(xs.tail, old, new))

def min_u24(a, b):
  if a < b:
    return a
  else:
    return b

def max_u24(a, b):
  if a > b:
    return a
  else:
    return b

# Comparator for required order: descending score, then ascending u, then ascending v
def comes_before_triple(t1, t2):
  (u1, v1, s1) = t1
  (u2, v2, s2) = t2
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

# Comparator for raw candidate dedup: ascending u, then ascending v, then descending score
def comes_before_cand_raw(t1, t2):
  (u1, v1, s1) = t1
  (u2, v2, s2) = t2
  if u1 < u2:
    return 1
  else:
    if u1 > u2:
      return 0
    else:
      if v1 < v2:
        return 1
      else:
        if v1 > v2:
          return 0
        else:
          if s1 > s2:
            return 1
          else:
            return 0

def list_length_tail(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return list_length_tail(xs.tail, acc + 1)

def list_length(xs):
  return list_length_tail(xs, 0)

def take_tail(xs, n, acc):
  if n == 0:
    return reverse_list(acc)
  else:
    match xs:
      case List/Nil:
        return reverse_list(acc)
      case List/Cons:
        return take_tail(xs.tail, n - 1, List/Cons(xs.head, acc))

def take(xs, n):
  return take_tail(xs, n, List/Nil)

def drop(xs, n):
  if n == 0:
    return xs
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        return drop(xs.tail, n - 1)

# Merge sort for triples using required comparator
def merge_triples_tail(a, b, acc):
  match a:
    case List/Nil:
      return reverse_acc(acc, b)
    case List/Cons:
      match b:
        case List/Nil:
          return reverse_acc(acc, a)
        case List/Cons:
          if comes_before_triple(a.head, b.head) == 1:
            return merge_triples_tail(a.tail, b, List/Cons(a.head, acc))
          else:
            return merge_triples_tail(a, b.tail, List/Cons(b.head, acc))

def merge_triples(a, b):
  return merge_triples_tail(a, b, List/Nil)

def merge_sort_triples(xs):
  len = list_length(xs)
  if len <= 1:
    return xs
  else:
    mid = len / 2
    left = take(xs, mid)
    right = drop(xs, mid)
    return merge_triples(merge_sort_triples(left), merge_sort_triples(right))

# Merge sort for raw candidates using cand_raw comparator
def merge_cand_raw_tail(a, b, acc):
  match a:
    case List/Nil:
      return reverse_acc(acc, b)
    case List/Cons:
      match b:
        case List/Nil:
          return reverse_acc(acc, a)
        case List/Cons:
          if comes_before_cand_raw(a.head, b.head) == 1:
            return merge_cand_raw_tail(a.tail, b, List/Cons(a.head, acc))
          else:
            return merge_cand_raw_tail(a, b.tail, List/Cons(b.head, acc))

def merge_cand_raw(a, b):
  return merge_cand_raw_tail(a, b, List/Nil)

def merge_sort_cand_raw(xs):
  len = list_length(xs)
  if len <= 1:
    return xs
  else:
    mid = len / 2
    left = take(xs, mid)
    right = drop(xs, mid)
    return merge_cand_raw(merge_sort_cand_raw(left), merge_sort_cand_raw(right))

# Deduplicate sorted raw candidates and accept those with score >= tau
def dedup_accept_sorted_tail(sorted, tau, prev_u, prev_v, acc):
  match sorted:
    case List/Nil:
      return reverse_list(acc)
    case List/Cons:
      (u, v, s) = sorted.head
      if prev_u == u:
        if prev_v == v:
          return dedup_accept_sorted_tail(sorted.tail, tau, u, v, acc)
        else:
          if s >= tau:
            return dedup_accept_sorted_tail(sorted.tail, tau, u, v, List/Cons(sorted.head, acc))
          else:
            return dedup_accept_sorted_tail(sorted.tail, tau, u, v, acc)
      else:
        if s >= tau:
          return dedup_accept_sorted_tail(sorted.tail, tau, u, v, List/Cons(sorted.head, acc))
        else:
          return dedup_accept_sorted_tail(sorted.tail, tau, u, v, acc)

def get_accepted_pairs(cands, tau, n):
  sorted_raw = merge_sort_cand_raw(cands)
  return dedup_accept_sorted_tail(sorted_raw, tau, n, n, List/Nil)

def has_mnl_conflict(rep, mnl, A, B):
  match mnl:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = mnl.head
      ra = list_get(rep, a)
      rb = list_get(rep, b)
      if ra == A:
        if rb == B:
          return 1
        else:
          return has_mnl_conflict(rep, mnl.tail, A, B)
      else:
        if ra == B:
          if rb == A:
            return 1
          else:
            return has_mnl_conflict(rep, mnl.tail, A, B)
        else:
          return has_mnl_conflict(rep, mnl.tail, A, B)

def process_pairs(pairs, rep, mnl):
  match pairs:
    case List/Nil:
      return rep
    case List/Cons:
      (u, v, s) = pairs.head
      ru = list_get(rep, u)
      rv = list_get(rep, v)
      if ru == rv:
        return process_pairs(pairs.tail, rep, mnl)
      else:
        if has_mnl_conflict(rep, mnl, ru, rv) == 1:
          return process_pairs(pairs.tail, rep, mnl)
        else:
          new_rep = replace_all(rep, rv, ru)
          return process_pairs(pairs.tail, new_rep, mnl)

def build_maxs(i, n, rep, maxs):
  if i == n:
    return maxs
  else:
    r = list_get(rep, i)
    cur = list_get(maxs, r)
    if cur == n:
      new_maxs = list_set(maxs, r, i)
    else:
      if i > cur:
        new_maxs = list_set(maxs, r, i)
      else:
        new_maxs = maxs
    return build_maxs(i + 1, n, rep, new_maxs)

def build_canons(i, rep, maxs, acc):
  if i == 0:
    return List/Cons(list_get(maxs, list_get(rep, 0)), acc)
  else:
    c = list_get(maxs, list_get(rep, i))
    return build_canons(i - 1, rep, maxs, List/Cons(c, acc))

def map_edges_acc(edges, canons, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      cu = list_get(canons, u)
      cv = list_get(canons, v)
      if cu == cv:
        return map_edges_acc(edges.tail, canons, acc)
      else:
        lo = min_u24(cu, cv)
        hi = max_u24(cu, cv)
        return map_edges_acc(edges.tail, canons, List/Cons((lo, hi), acc))

def comes_before_pair(p1, p2):
  (x1, y1) = p1
  (x2, y2) = p2
  if x1 < x2:
    return 1
  else:
    if x1 > x2:
      return 0
    else:
      if y1 < y2:
        return 1
      else:
        return 0

def merge_pairs_tail(a, b, acc):
  match a:
    case List/Nil:
      return reverse_acc(acc, b)
    case List/Cons:
      match b:
        case List/Nil:
          return reverse_acc(acc, a)
        case List/Cons:
          if comes_before_pair(a.head, b.head) == 1:
            return merge_pairs_tail(a.tail, b, List/Cons(a.head, acc))
          else:
            return merge_pairs_tail(a, b.tail, List/Cons(b.head, acc))

def merge_pairs(a, b):
  return merge_pairs_tail(a, b, List/Nil)

def merge_sort_pairs(xs):
  len = list_length(xs)
  if len <= 1:
    return xs
  else:
    mid = len / 2
    left = take(xs, mid)
    right = drop(xs, mid)
    return merge_pairs(merge_sort_pairs(left), merge_sort_pairs(right))

def dedupe_adjacent_pairs(xs, acc):
  match xs:
    case List/Nil:
      return reverse_list(acc)
    case List/Cons:
      (x, y) = xs.head
      match acc:
        case List/Nil:
          return dedupe_adjacent_pairs(xs.tail, List/Cons(xs.head, acc))
        case List/Cons:
          (px, py) = acc.head
          if px == x:
            if py == y:
              return dedupe_adjacent_pairs(xs.tail, acc)
            else:
              return dedupe_adjacent_pairs(xs.tail, List/Cons(xs.head, acc))
          else:
            return dedupe_adjacent_pairs(xs.tail, List/Cons(xs.head, acc))

def contains_u24(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains_u24(xs.tail, x)

def add_unique_u24(acc, x):
  if contains_u24(acc, x) == 1:
    return acc
  else:
    return List/Cons(x, acc)

def uniq_u24(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      new_acc = add_unique_u24(acc, xs.head)
      return uniq_u24(xs.tail, new_acc)

def merge_u24_tail(a, b, acc):
  match a:
    case List/Nil:
      return reverse_acc(acc, b)
    case List/Cons:
      match b:
        case List/Nil:
          return reverse_acc(acc, a)
        case List/Cons:
          if a.head < b.head:
            return merge_u24_tail(a.tail, b, List/Cons(a.head, acc))
          else:
            return merge_u24_tail(a, b.tail, List/Cons(b.head, acc))

def merge_u24(a, b):
  return merge_u24_tail(a, b, List/Nil)

def merge_sort_u24(xs):
  len = list_length(xs)
  if len <= 1:
    return xs
  else:
    mid = len / 2
    left = take(xs, mid)
    right = drop(xs, mid)
    return merge_u24(merge_sort_u24(left), merge_sort_u24(right))

def gather_values(attrs, canons, cluster, key, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, k, val) = attrs.head
      if list_get(canons, node) == cluster:
        if k == key:
          return gather_values(attrs.tail, canons, cluster, key, List/Cons(val, acc))
        else:
          return gather_values(attrs.tail, canons, cluster, key, acc)
      else:
        return gather_values(attrs.tail, canons, cluster, key, acc)

def count_val(xs, v):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == v:
        return 1 + count_val(xs.tail, v)
      else:
        return count_val(xs.tail, v)

def mode_helper(remaining, all_vals, best_val, best_count):
  match remaining:
    case List/Nil:
      return best_val
    case List/Cons:
      v = remaining.head
      cnt = count_val(all_vals, v)
      if cnt > best_count:
        return mode_helper(remaining.tail, all_vals, v, cnt)
      else:
        if cnt == best_count:
          if v < best_val:
            return mode_helper(remaining.tail, all_vals, v, cnt)
          else:
            return mode_helper(remaining.tail, all_vals, best_val, best_count)
        else:
          return mode_helper(remaining.tail, all_vals, best_val, best_count)

def mode_value(vals):
  return mode_helper(vals, vals, 0, 0)

def is_empty(xs):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      return 0

def add_one_key(cluster, key, attrs, canons, acc):
  vals = gather_values(attrs, canons, cluster, key, List/Nil)
  if is_empty(vals) == 1:
    return acc
  else:
    mval = mode_value(vals)
    return List/Cons((cluster, key, mval), acc)

def add_key_triples(cluster, attrs, canons, acc):
  acc1 = add_one_key(cluster, 0, attrs, canons, acc)
  acc2 = add_one_key(cluster, 1, attrs, canons, acc1)
  acc3 = add_one_key(cluster, 2, attrs, canons, acc2)
  acc4 = add_one_key(cluster, 3, attrs, canons, acc3)
  return acc4

def generate_P(clusters, attrs, canons, acc):
  match clusters:
    case List/Nil:
      return acc
    case List/Cons:
      new_acc = add_key_triples(clusters.head, attrs, canons, acc)
      return generate_P(clusters.tail, attrs, canons, new_acc)

def comes_before_attr(t1, t2):
  (c1, k1, v1) = t1
  (c2, k2, v2) = t2
  if c1 < c2:
    return 1
  else:
    if c1 > c2:
      return 0
    else:
      if k1 < k2:
        return 1
      else:
        if k1 > k2:
          return 0
        else:
          if v1 < v2:
            return 1
          else:
            return 0

def merge_attrs_tail(a, b, acc):
  match a:
    case List/Nil:
      return reverse_acc(acc, b)
    case List/Cons:
      match b:
        case List/Nil:
          return reverse_acc(acc, a)
        case List/Cons:
          if comes_before_attr(a.head, b.head) == 1:
            return merge_attrs_tail(a.tail, b, List/Cons(a.head, acc))
          else:
            return merge_attrs_tail(a, b.tail, List/Cons(b.head, acc))

def merge_attrs(a, b):
  return merge_attrs_tail(a, b, List/Nil)

def merge_sort_attrs(xs):
  len = list_length(xs)
  if len <= 1:
    return xs
  else:
    mid = len / 2
    left = take(xs, mid)
    right = drop(xs, mid)
    return merge_attrs(merge_sort_attrs(left), merge_sort_attrs(right))

def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  if n == 0:
    return (List/Nil, List/Nil, List/Nil)
  else:
    accepted = get_accepted_pairs(cands, tau, n)
    sorted_accepted = merge_sort_triples(accepted)
    rep0 = range(n, List/Nil)
    rep_final = process_pairs(sorted_accepted, rep0, mnl)
    maxs0 = repeat(n, n)
    maxs = build_maxs(0, n, rep_final, maxs0)
    canons = build_canons(n - 1, rep_final, maxs, List/Nil)

    mapped_edges = map_edges_acc(edges, canons, List/Nil)
    sorted_edges = merge_sort_pairs(mapped_edges)
    deduped_edges_rev = dedupe_adjacent_pairs(sorted_edges, List/Nil)
    E = deduped_edges_rev

    cluster_ids_rev = uniq_u24(canons, List/Nil)
    cluster_ids_unsorted = reverse_list(cluster_ids_rev)
    clusters = merge_sort_u24(cluster_ids_unsorted)
    p_rev = generate_P(clusters, attrs, canons, List/Nil)
    P = merge_sort_attrs(p_rev)

    return (canons, E, P)
