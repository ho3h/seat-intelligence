def prog(xs):
  return radix_sort(xs, 0)

def radix_sort(xs, bit):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          if bit == 24:
            return xs
          else:
            shift = 23 - bit
            (zeros, ones, uniform) = split_bit(xs, shift, xs.head)
            if uniform == 1:
              return xs
            else:
              match zeros:
                case List/Nil:
                  return radix_sort(ones, bit + 1)
                case List/Cons:
                  match ones:
                    case List/Nil:
                      return radix_sort(zeros, bit + 1)
                    case List/Cons:
                      sorted_zeros = radix_sort(zeros, bit + 1)
                      sorted_ones = radix_sort(ones, bit + 1)
                      return append(sorted_zeros, sorted_ones)

def split_bit(xs, shift, pivot):
  match xs:
    case List/Nil:
      return ([], [], 1)
    case List/Cons:
      (zeros, ones, uniform) = split_bit(xs.tail, shift, pivot)
      if ((xs.head >> shift) & 1) == 0:
        if xs.head == pivot:
          return (List/Cons(xs.head, zeros), ones, uniform)
        else:
          return (List/Cons(xs.head, zeros), ones, 0)
      else:
        if xs.head == pivot:
          return (zeros, List/Cons(xs.head, ones), uniform)
        else:
          return (zeros, List/Cons(xs.head, ones), 0)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
