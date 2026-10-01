def prog(x):
  (tau, cands) = x
  accepted = filter_scores(cands, tau)
  return radix(accepted, 0, 9)

def filter_scores(xs, tau):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = filter_scores(xs.tail, tau)
      (u, v, score) = xs.head
      if score >= tau:
        return List/Cons(xs.head, rest)
      else:
        return rest

def all_same(xs):
  match xs:
    case List/Nil:
      return True
    case List/Cons:
      return same_tail(xs.tail, xs.head)

def same_tail(xs, first):
  match xs:
    case List/Nil:
      return True
    case List/Cons:
      (u, v, score) = first
      (hu, hv, hscore) = xs.head
      if u == hu:
        if v == hv:
          if score == hscore:
            return same_tail(xs.tail, first)
          else:
            return False
        else:
          return False
      else:
        return False

def advance(field, bit):
  if bit > 0:
    return (field, bit - 1)
  else:
    if field == 0:
      return (1, 23)
    else:
      if field == 1:
        return (2, 23)
      else:
        return (3, 0)

def partition(xs, field, bit):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (zeros, ones) = partition(xs.tail, field, bit)
      (u, v, score) = xs.head
      if field == 0:
        if ((score >> bit) & 1) == 0:
          return (List/Cons(xs.head, zeros), ones)
        else:
          return (zeros, List/Cons(xs.head, ones))
      else:
        if field == 1:
          if ((u >> bit) & 1) == 0:
            return (List/Cons(xs.head, zeros), ones)
          else:
            return (zeros, List/Cons(xs.head, ones))
        else:
          if ((v >> bit) & 1) == 0:
            return (List/Cons(xs.head, zeros), ones)
          else:
            return (zeros, List/Cons(xs.head, ones))

def radix(xs, field, bit):
  if field == 3:
    return xs
  else:
    match xs:
      case List/Nil:
        return List/Nil
      case List/Cons:
        match xs.tail:
          case List/Nil:
            return xs
          case List/Cons:
            if all_same(xs):
              return xs
            else:
              (zeros, ones) = partition(xs, field, bit)
              (next_field, next_bit) = advance(field, bit)
              match zeros:
                case List/Nil:
                  return radix(ones, next_field, next_bit)
                case List/Cons:
                  match ones:
                    case List/Nil:
                      return radix(zeros, next_field, next_bit)
                    case List/Cons:
                      sorted_zeros = radix(zeros, next_field, next_bit)
                      sorted_ones = radix(ones, next_field, next_bit)
                      if field == 0:
                        return append(sorted_ones, sorted_zeros)
                      else:
                        return append(sorted_zeros, sorted_ones)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
