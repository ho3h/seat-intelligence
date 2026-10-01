def prog(x):
  (pred, truth) = x
  pairs = make_pairs(pred, truth)
  sorted_pred = sort_pairs(pairs, 0)
  sorted_truth = sort_pairs(pairs, 1)
  sorted_both = sort_pairs(pairs, 2)
  same_pred = run_total(sorted_pred, 0)
  same_truth = run_total(sorted_truth, 1)
  same_both = run_total(sorted_both, 2)
  n = list_length(pairs, 0)
  total = choose_two(n)
  return total - same_pred - same_truth + 2 * same_both

def make_pairs(pred, truth):
  match pred:
    case List/Nil:
      return []
    case List/Cons:
      match truth:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons((pred.head, truth.head), make_pairs(pred.tail, truth.tail))

def list_length(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return list_length(xs.tail, acc + 1)

def choose_two(n):
  if n % 2 == 0:
    return (n / 2) * (n - 1)
  else:
    return n * ((n - 1) / 2)

def split_pairs(xs, turn):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_pairs(xs.tail, 1 - turn)
      if turn == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def sort_pairs(xs, mode):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs, 0)
          sorted_left = sort_pairs(left, mode)
          sorted_right = sort_pairs(right, mode)
          return merge_pairs(sorted_left, sorted_right, mode)

def merge_pairs(left, right, mode):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          if pair_less(left.head, right.head, mode):
            return List/Cons(left.head, merge_pairs(left.tail, right, mode))
          else:
            return List/Cons(right.head, merge_pairs(left, right.tail, mode))

def pair_less(a, b, mode):
  (ap, at) = a
  (bp, bt) = b
  if mode == 0:
    return ap < bp
  else:
    if mode == 1:
      return at < bt
    else:
      if ap < bp:
        return ap < bp
      else:
        if ap == bp:
          return at < bt
        else:
          return ap < bp

def run_total(xs, mode):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return run_more(xs.tail, xs.head, 1, 0, mode)

def run_more(xs, key, count, acc, mode):
  match xs:
    case List/Nil:
      return acc + choose_two(count)
    case List/Cons:
      if pair_equal(xs.head, key, mode):
        return run_more(xs.tail, key, count + 1, acc, mode)
      else:
        return run_more(xs.tail, xs.head, 1, acc + choose_two(count), mode)

def pair_equal(a, b, mode):
  (ap, at) = a
  (bp, bt) = b
  if mode == 0:
    return ap == bp
  else:
    if mode == 1:
      return at == bt
    else:
      if ap == bp:
        return at == bt
      else:
        return ap == bp
