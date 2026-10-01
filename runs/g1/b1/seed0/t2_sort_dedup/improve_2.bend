def prog(xs):
  return radix(xs, 23)

def radix(xs, bit):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (zeros, ones, uniform) = split_bit(xs, bit, xs.head)
      if uniform:
        return [xs.head]
      else:
        if bit == 0:
          return final_values(zeros, ones)
        else:
          match zeros:
            case List/Nil:
              return radix(ones, bit - 1)
            case List/Cons:
              match ones:
                case List/Nil:
                  return radix(zeros, bit - 1)
                case List/Cons:
                  sorted_zeros = radix(zeros, bit - 1)
                  sorted_ones = radix(ones, bit - 1)
                  return append_lists(sorted_zeros, sorted_ones)

def split_bit(xs, bit, representative):
  match xs:
    case List/Nil:
      return ([], [], true)
    case List/Cons:
      (zeros, ones, uniform_tail) = split_bit(xs.tail, bit, representative)
      if xs.head == representative:
        uniform = uniform_tail
      else:
        uniform = false
      if ((xs.head >> bit) & 1) == 0:
        return (List/Cons(xs.head, zeros), ones, uniform)
      else:
        return (zeros, List/Cons(xs.head, ones), uniform)

def final_values(zeros, ones):
  match zeros:
    case List/Nil:
      match ones:
        case List/Nil:
          return []
        case List/Cons:
          return [ones.head]
    case List/Cons:
      match ones:
        case List/Nil:
          return [zeros.head]
        case List/Cons:
          return [zeros.head, ones.head]

def append_lists(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_lists(a.tail, b))
