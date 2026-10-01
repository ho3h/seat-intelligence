def prog(x):
  (pred, truth) = x
  pairs = zip_pairs(pred, truth)
  sorted_pairs = sort_pairs(pairs)
  (tp, pred_pairs) = pair_stats(sorted_pairs)
  sorted_truth = sort_nums(truth)
  truth_pairs = num_stats(sorted_truth)
  return (tp, pred_pairs - tp, truth_pairs - tp)

def zip_pairs(pred, truth):
  match pred:
    case List/Nil:
      return []
    case List/Cons:
      match truth:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons((pred.head, truth.head), zip_pairs(pred.tail, truth.tail))

def split_pairs(xs, turn, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_pairs(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_pairs(xs.tail, 0, left, List/Cons(xs.head, right))

def pair_less(a, b):
  (ap, at) = a
  (bp, bt) = b
  if ap < bp:
    return 1
  else:
    if ap == bp:
      if at < bt:
        return 1
      else:
        return 0
    else:
      return 0

def sort_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs, 0, [], [])
          return merge_pairs(sort_pairs(left), sort_pairs(right))

def merge_pairs(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if pair_less(a.head, b.head) == 1:
            return List/Cons(a.head, merge_pairs(a.tail, b))
          else:
            return List/Cons(b.head, merge_pairs(a, b.tail))

def choose_two(n):
  return (n * (n - 1)) / 2

def pair_stats(xs):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      (p, t) = xs.head
      return scan_pairs(xs.tail, p, t, 1, 1, 0, 0)

def scan_pairs(xs, current_p, current_t, cell_count, pred_count, tp, pred_pairs):
  match xs:
    case List/Nil:
      return (tp + choose_two(cell_count), pred_pairs + choose_two(pred_count))
    case List/Cons:
      (p, t) = xs.head
      if p == current_p:
        if t == current_t:
          return scan_pairs(xs.tail, current_p, current_t, cell_count + 1, pred_count + 1, tp, pred_pairs)
        else:
          return scan_pairs(xs.tail, current_p, t, 1, pred_count + 1, tp + choose_two(cell_count), pred_pairs)
      else:
        return scan_pairs(xs.tail, p, t, 1, 1, tp + choose_two(cell_count), pred_pairs + choose_two(pred_count))

def split_nums(xs, turn, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_nums(xs.tail, 1, List/Cons(xs.head, left), right)
      else:
        return split_nums(xs.tail, 0, left, List/Cons(xs.head, right))

def sort_nums(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_nums(xs, 0, [], [])
          return merge_nums(sort_nums(left), sort_nums(right))

def merge_nums(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head <= b.head:
            return List/Cons(a.head, merge_nums(a.tail, b))
          else:
            return List/Cons(b.head, merge_nums(a, b.tail))

def num_stats(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return scan_nums(xs.tail, xs.head, 1, 0)

def scan_nums(xs, current, count, total):
  match xs:
    case List/Nil:
      return total + choose_two(count)
    case List/Cons:
      if xs.head == current:
        return scan_nums(xs.tail, current, count + 1, total)
      else:
        return scan_nums(xs.tail, xs.head, 1, total + choose_two(count))
