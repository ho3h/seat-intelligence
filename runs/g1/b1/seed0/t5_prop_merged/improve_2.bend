def prog(x):
  (clusters, attrs) = x
  normalized = normalize_attrs(attrs, clusters)
  ordered = sort_triples(normalized)
  return emit_groups(ordered)

def get_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_at(xs.tail, index - 1)

def normalize_attrs(attrs, clusters):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      canonical = get_at(clusters, node)
      return List/Cons((canonical, key, value), normalize_attrs(attrs.tail, clusters))

def split_alternate(xs, turn):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alternate(xs.tail, 1 - turn)
      if turn == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def sort_triples(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternate(xs, 0)
          sorted_left = sort_triples(left)
          sorted_right = sort_triples(right)
          return merge_triples(sorted_left, sorted_right)

def triple_less(a, b):
  (ac, ak, av) = a
  (bc, bk, bv) = b
  if ac < bc:
    return 1
  else:
    if ac > bc:
      return 0
    else:
      if ak < bk:
        return 1
      else:
        if ak > bk:
          return 0
        else:
          if av < bv:
            return 1
          else:
            return 0

def merge_triples(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if triple_less(left.head, right.head) == 1:
            return List/Cons(left.head, merge_triples(left.tail, right))
          else:
            return List/Cons(right.head, merge_triples(left, right.tail))

def choose_best(best_value, best_count, value, count):
  if count > best_count:
    return (value, count)
  else:
    if count == best_count:
      if value < best_value:
        return (value, count)
      else:
        return (best_value, best_count)
    else:
      return (best_value, best_count)

def emit_groups(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (canonical, key, value) = xs.head
      return process_group(xs.tail, canonical, key, value, 1, value, 0)

def process_group(xs, canonical, key, run_value, run_count, best_value, best_count):
  match xs:
    case List/Nil:
      (winner, winner_count) = choose_best(best_value, best_count, run_value, run_count)
      return List/Cons((canonical, key, winner), [])
    case List/Cons:
      (next_canonical, next_key, next_value) = xs.head
      if next_canonical == canonical:
        if next_key == key:
          if next_value == run_value:
            return process_group(xs.tail, canonical, key, run_value, run_count + 1, best_value, best_count)
          else:
            (new_best_value, new_best_count) = choose_best(best_value, best_count, run_value, run_count)
            return process_group(xs.tail, canonical, key, next_value, 1, new_best_value, new_best_count)
        else:
          (winner, winner_count) = choose_best(best_value, best_count, run_value, run_count)
          return List/Cons((canonical, key, winner), emit_groups(xs))
      else:
        (winner, winner_count) = choose_best(best_value, best_count, run_value, run_count)
        return List/Cons((canonical, key, winner), emit_groups(xs))
