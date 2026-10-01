def prog(x):
  (lo, hi, xs) = x
  return count_in_range(lo, hi, xs, 0)

def count_in_range(lo, hi, xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      a = xs.head
      rest1 = xs.tail
      match rest1:
        case List/Nil:
          return acc + ((a >= lo) & (a <= hi))
        case List/Cons:
          b = rest1.head
          rest2 = rest1.tail
          match rest2:
            case List/Nil:
              return acc + ((a >= lo) & (a <= hi)) + ((b >= lo) & (b <= hi))
            case List/Cons:
              c = rest2.head
              rest3 = rest2.tail
              match rest3:
                case List/Nil:
                  return acc + ((a >= lo) & (a <= hi)) + ((b >= lo) & (b <= hi)) + ((c >= lo) & (c <= hi))
                case List/Cons:
                  d = rest3.head
                  return count_in_range(lo, hi, rest3.tail, acc + ((a >= lo) & (a <= hi)) + ((b >= lo) & (b <= hi)) + ((c >= lo) & (c <= hi)) + ((d >= lo) & (d <= hi)))
