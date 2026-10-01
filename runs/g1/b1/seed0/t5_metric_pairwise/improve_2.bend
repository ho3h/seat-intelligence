def prog(x):
  (pred, truth) = x
  pairs = zip_pairs(pred, truth)
  tp = pair_freq(pairs)
  pred_pairs = one_freq(pairs, 0)
  truth_pairs = one_freq(pairs, 1)
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

def choose_two(n):
  return (n * (n - 1)) / 2

def find_bit(mask, bit):
  if bit >= 24:
    return 0
  else:
    if (mask & (1 << bit)) != 0:
      return bit
    else:
      return find_bit(mask, bit + 1)

def scan_pair_diff(xs, p0, t0, mp, mt, count):
  match xs:
    case List/Nil:
      return (mp, mt, count)
    case List/Cons:
      (p, t) = xs.head
      return scan_pair_diff(xs.tail, p0, t0, mp | (p ^ p0), mt | (t ^ t0), count + 1)

def partition_pairs(xs, field, bit, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      (p, t) = xs.head
      if field == 0:
        if ((p >> bit) & 1) == 0:
          return partition_pairs(xs.tail, field, bit, List/Cons(xs.head, left), right)
        else:
          return partition_pairs(xs.tail, field, bit, left, List/Cons(xs.head, right))
      else:
        if ((t >> bit) & 1) == 0:
          return partition_pairs(xs.tail, field, bit, List/Cons(xs.head, left), right)
        else:
          return partition_pairs(xs.tail, field, bit, left, List/Cons(xs.head, right))

def pair_freq(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (p0, t0) = xs.head
      (mp, mt, count) = scan_pair_diff(xs, p0, t0, 0, 0, 0)
      if mp == 0:
        if mt == 0:
          return choose_two(count)
        else:
          bit = find_bit(mt, 0)
          (left, right) = partition_pairs(xs, 1, bit, [], [])
          return pair_freq(left) + pair_freq(right)
      else:
        bit = find_bit(mp, 0)
        (left, right) = partition_pairs(xs, 0, bit, [], [])
        return pair_freq(left) + pair_freq(right)

def label_of(pair, field):
  (p, t) = pair
  if field == 0:
    return p
  else:
    return t

def scan_one(xs, field, base, mask, count):
  match xs:
    case List/Nil:
      return (mask, count)
    case List/Cons:
      value = label_of(xs.head, field)
      return scan_one(xs.tail, field, base, mask | (value ^ base), count + 1)

def partition_one(xs, field, bit, left, right):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      value = label_of(xs.head, field)
      if ((value >> bit) & 1) == 0:
        return partition_one(xs.tail, field, bit, List/Cons(xs.head, left), right)
      else:
        return partition_one(xs.tail, field, bit, left, List/Cons(xs.head, right))

def one_freq(xs, field):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      base = label_of(xs.head, field)
      (mask, count) = scan_one(xs, field, base, 0, 0)
      if mask == 0:
        return choose_two(count)
      else:
        bit = find_bit(mask, 0)
        (left, right) = partition_one(xs, field, bit, [], [])
        return one_freq(left, field) + one_freq(right, field)
