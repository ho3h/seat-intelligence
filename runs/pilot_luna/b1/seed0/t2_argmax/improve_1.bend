def prog(xs):
  return scan(xs, 0, 0, 0)

def scan(xs, index, best, best_index):
  match xs:
    case List/Nil:
      return best_index
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head > best:
            return index
          else:
            return best_index
        case List/Cons:
          if xs.head > best:
            best1 = xs.head
            best_index1 = index
          else:
            best1 = best
            best_index1 = best_index
          if xs.tail.head > best1:
            return scan(xs.tail.tail, index + 2, xs.tail.head, index + 1)
          else:
            return scan(xs.tail.tail, index + 2, best1, best_index1)
