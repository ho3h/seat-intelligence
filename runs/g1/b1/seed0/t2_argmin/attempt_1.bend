def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return argmin_scan(xs.tail, 1, xs.head, 0)

def argmin_scan(xs, idx, best, best_idx):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      if xs.head < best:
        return argmin_scan(xs.tail, idx + 1, xs.head, idx)
      else:
        return argmin_scan(xs.tail, idx + 1, best, best_idx)
