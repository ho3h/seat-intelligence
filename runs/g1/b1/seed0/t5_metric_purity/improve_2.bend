def prog(x):
  (pred, truth) = x
  pairs = make_pairs(pred, truth)
  return radix_pred(pairs, 0)

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

def split4(xs, kind, bit):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil, List/Nil, List/Nil)
    case List/Cons:
      (a, b, c, d) = split4(xs.tail, kind, bit)
      (p, t) = xs.head
      if kind == 0:
        digit = (p >> bit) & 3
      else:
        digit = (t >> bit) & 3
      if digit == 0:
        return (List/Cons(xs.head, a), b, c, d)
      else:
        if digit == 1:
          return (a, List/Cons(xs.head, b), c, d)
        else:
          if digit == 2:
            return (a, b, List/Cons(xs.head, c), d)
          else:
            return (a, b, c, List/Cons(xs.head, d))

def radix_pred(xs, level):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if level == 12:
        return radix_truth(xs, 0)
      else:
        bit = 22 - level * 2
        (a, b, c, d) = split4(xs, 0, bit)
        va = radix_pred(a, level + 1)
        vb = radix_pred(b, level + 1)
        vc = radix_pred(c, level + 1)
        vd = radix_pred(d, level + 1)
        return va + vb + vc + vd

def radix_truth(xs, level):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if level == 12:
        return count_items(xs)
      else:
        bit = 22 - level * 2
        (a, b, c, d) = split4(xs, 1, bit)
        va = radix_truth(a, level + 1)
        vb = radix_truth(b, level + 1)
        vc = radix_truth(c, level + 1)
        vd = radix_truth(d, level + 1)
        return max2(max2(va, vb), max2(vc, vd))

def count_items(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + count_items(xs.tail)

def max2(a, b):
  if a > b:
    return a
  else:
    return b
