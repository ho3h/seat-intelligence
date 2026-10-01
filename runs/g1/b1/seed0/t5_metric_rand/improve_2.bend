def prog(x):
  (pred, truth) = x
  pairs = make_pairs(pred, truth)
  same_pred = same_labels(pred, 23)
  same_truth = same_labels(truth, 23)
  same_both = same_pairs(pairs, 47)
  n = list_length(pred)
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

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def choose_two(n):
  if n % 2 == 0:
    return (n / 2) * (n - 1)
  else:
    return n * ((n - 1) / 2)

def split_labels(xs, bit):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zeros, ones) = split_labels(xs.tail, bit)
      if ((xs.head >> bit) & 1) == 0:
        return (List/Cons(xs.head, zeros), ones)
      else:
        return (zeros, List/Cons(xs.head, ones))

def same_labels(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return 0
        case List/Cons:
          (zeros, ones) = split_labels(xs, bit)
          if bit == 0:
            return choose_two(list_length(zeros)) + choose_two(list_length(ones))
          else:
            return same_labels(zeros, bit - 1) + same_labels(ones, bit - 1)

def split_pairs(xs, bit):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (p, t) = xs.head
      (zeros, ones) = split_pairs(xs.tail, bit)
      if bit >= 24:
        value = (p >> (bit - 24)) & 1
      else:
        value = (t >> bit) & 1
      if value == 0:
        return (List/Cons(xs.head, zeros), ones)
      else:
        return (zeros, List/Cons(xs.head, ones))

def same_pairs(xs, bit):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return 0
        case List/Cons:
          (zeros, ones) = split_pairs(xs, bit)
          if bit == 0:
            return choose_two(list_length(zeros)) + choose_two(list_length(ones))
          else:
            return same_pairs(zeros, bit - 1) + same_pairs(ones, bit - 1)
