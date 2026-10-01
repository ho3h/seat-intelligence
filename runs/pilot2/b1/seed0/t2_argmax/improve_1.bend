def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return scan(xs.tail, 1, 0, xs.head)

def scan(xs, idx, best_idx, best_val):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      tail = xs.tail
      if xs.head > best_val:
        match tail:
          case List/Nil:
            return idx
          case List/Cons:
            if tail.head > xs.head:
              return scan(tail.tail, idx + 2, idx + 1, tail.head)
            else:
              return scan(tail.tail, idx + 2, idx, xs.head)
      else:
        match tail:
          case List/Nil:
            return best_idx
          case List/Cons:
            if tail.head > best_val:
              return scan(tail.tail, idx + 2, idx + 1, tail.head)
            else:
              return scan(tail.tail, idx + 2, best_idx, best_val)
