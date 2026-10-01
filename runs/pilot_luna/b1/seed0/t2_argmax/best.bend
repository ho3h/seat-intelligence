def prog(xs):
  return scan(xs, 0, 0, 0)

def scan(xs, index, best, best_index):
  match xs:
    case List/Nil:
      return best_index
    case List/Cons:
      if xs.head > best:
        return scan(xs.tail, index + 1, xs.head, index)
      else:
        return scan(xs.tail, index + 1, best, best_index)
