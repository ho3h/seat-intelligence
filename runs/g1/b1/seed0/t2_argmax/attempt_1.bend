def prog(xs):
  return scan(xs, 0, 0, 0)

def scan(xs, i, best_i, best_v):
  match xs:
    case List/Nil:
      return best_i
    case List/Cons:
      if xs.head > best_v:
        return scan(xs.tail, i + 1, i, xs.head)
      else:
        return scan(xs.tail, i + 1, best_i, best_v)
