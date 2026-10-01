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

# Flat array helpers
def flat_index(n, i, j):
  return i * n + j

def flat_get(flat, n, i, j):
  return list_get(flat, flat_index(n, i, j))

def flat_set(flat, n, i, j, val):
  return list_set(flat, flat_index(n, i, j), val)

# Process candidates: keep highest score per (u,v)
def process_cands(cands, n, scores):
  match cands:
    case List/Nil:
      return scores
    case List/Cons:
      (u, v, s) = cands.head
      cur = flat_get(scores, n, u, v)
      if s > cur:
        scores_new = flat_set(scores, n, u, v, s)
      else:
        scores_new = scores
      return process_cands(cands.tail, n, scores_new)

# Generate accepted pairs in required order using scores table
def generate_accepted(n, tau, scores, out):
  def score_loop(score, out):
    if score < 0:
      return out
    else:
      def u_loop(u, out):
        if u == n:
          return out
        else:
          def v_loop(v, out):
            if v == n:
              return out
            else:
              s = flat_get(scores, n, u, v)
              if s == score:
                if s >= tau:
                  out_new = List/Cons((u, v, s), out)
                else:
                  out_new = out
              else:
                out_new = out
              return v_loop(v + 1, out_new)
          return v_loop(u + 1, out)
      out1 = u_loop(0, out)
      return score_loop(score - 1, out1)
  return reverse_list(score_loop(1000, out))

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

def map_edges_to_flat(edges, canons, n, edge_exists):
  match edges:
    case List/Nil:
      return edge_exists
    case List/Cons:
      (u, v) = edges.head
      cu = list_get(canons, u)
      cv = list_get(canons, v)
      if cu == cv:
        return map_edges_to_flat(edges.tail, canons, n, edge_exists)
      else:
        lo = min_u24(cu, cv)
        hi = max_u24(cu, cv)
        new_flat = flat_set(edge_exists, n, lo, hi, 1)
        return map_edges_to_flat(edges.tail, canons, n, new_flat)

def generate_edges(n, edge_exists, out):
  def lo_loop(lo, out):
    if lo == n:
      return out
    else:
      def hi_loop(hi, out):
        if hi == n:
          return out
        else:
          if flat_get(edge_exists, n, lo, hi) == 1:
            out_new = List/Cons((lo, hi), out)
          else:
            out_new = out
          return hi_loop(hi + 1, out_new)
      out1 = hi_loop(lo + 1, out)
      return lo_loop(lo + 1, out1)
  return reverse_list(lo_loop(0, out))

def collect_values(attrs, canons, cluster, key, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, k, val) = attrs.head
      if list_get(canons, node) == cluster:
        if k == key:
          return collect_values(attrs.tail, canons, cluster, key, List/Cons(val, acc))
        else:
          return collect_values(attrs.tail, canons, cluster, key, acc)
      else:
        return collect_values(attrs.tail, canons, cluster, key, acc)

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
  vals = collect_values(attrs, canons, cluster, key, List/Nil)
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

def generate_P(n, attrs, canons, out):
  def cluster_loop(c, out):
    if c == n:
      return out
    else:
      if list_get(canons, c) == c:  # c is a canonical id if it appears
        out_new = add_key_triples(c, attrs, canons, out)
      else:
        out_new = out
      return cluster_loop(c + 1, out_new)
  return reverse_list(cluster_loop(0, out))

def prog(x):
  (n, tau, mnl, cands, edges, attrs) = x
  if n == 0:
    return (List/Nil, List/Nil, List/Nil)
  else:
    # 1. Deduplicate candidates and keep max score per (u,v)
    scores = repeat(0, n * n)
    scores = process_cands(cands, n, scores)
    accepted = generate_accepted(n, tau, scores, List/Nil)

    # 2. Process merges
    rep0 = range(n, List/Nil)
    rep_final = process_pairs(accepted, rep0, mnl)

    # 3. Build canonical ids
    maxs0 = repeat(n, n)
    maxs = build_maxs(0, n, rep_final, maxs0)
    canons = build_canons(n - 1, rep_final, maxs, List/Nil)

    # 4. Rewrite edges
    edge_exists = repeat(0, n * n)
    edge_exists = map_edges_to_flat(edges, canons, n, edge_exists)
    E = generate_edges(n, edge_exists, List/Nil)

    # 5. Build attribute triples
    P = generate_P(n, attrs, canons, List/Nil)

    return (canons, E, P)
