def prog(x):
  (pred, truth) = x
  pairs = make_pairs(pred, truth)
  sorted_pairs = merge_sort(pairs)
  return consume_pairs(sorted_pairs, 0, 0, 0, 0, 0, 0)

def make_pairs(pred, truth):
  match pred:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match truth:
        case List/Nil:
          return List/Nil
        case List/Cons:
          rest = make_pairs(pred.tail, truth.tail)
          return List/Cons((pred.head, truth.head), rest)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return (List/Cons(xs.head, List/Nil), List/Nil)
        case List/Cons:
          (left, right) = split_pairs(tail.tail)
          return (List/Cons(xs.head, left), List/Cons(tail.head, right))

def pair_less(a, b):
  (p, t) = a
  (q, u) = b
  if p < q:
    return 1
  else:
    if p > q:
      return 0
    else:
      if t <= u:
        return 1
      else:
        return 0

def merge_pairs(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if pair_less(xs.head, ys.head) == 1:
            rest = merge_pairs(xs.tail, ys)
            return List/Cons(xs.head, rest)
          else:
            rest = merge_pairs(xs, ys.tail)
            return List/Cons(ys.head, rest)

def merge_sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      tail = xs.tail
      match tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_pairs(sorted_left, sorted_right)

def consume_pairs(xs, have, current_pred, current_truth, pair_count, best, total):
  match xs:
    case List/Nil:
      if have == 0:
        return total
      else:
        if pair_count > best:
          return total + pair_count
        else:
          return total + best
    case List/Cons:
      (p, t) = xs.head
      if have == 0:
        return consume_pairs(xs.tail, 1, p, t, 1, 0, total)
      else:
        if p == current_pred:
          if t == current_truth:
            return consume_pairs(xs.tail, 1, current_pred, current_truth, pair_count + 1, best, total)
          else:
            if pair_count > best:
              return consume_pairs(xs.tail, 1, current_pred, t, 1, pair_count, total)
            else:
              return consume_pairs(xs.tail, 1, current_pred, t, 1, best, total)
        else:
          if pair_count > best:
            next_total = total + pair_count
          else:
            next_total = total + best
          return consume_pairs(xs.tail, 1, p, t, 1, 0, next_total)
