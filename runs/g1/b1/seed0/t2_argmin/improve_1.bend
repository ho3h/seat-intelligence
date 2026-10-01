def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return argmin_pairs(xs.tail, 1, xs.head, 0)

def argmin_pairs(xs, idx, best, best_idx):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      y = xs.tail
      match y:
        case List/Nil:
          if xs.head < best:
            return idx
          else:
            return best_idx
        case List/Cons:
          if xs.head <= y.head:
            if xs.head < best:
              return argmin_pairs(y.tail, idx + 2, xs.head, idx)
            else:
              return argmin_pairs(y.tail, idx + 2, best, best_idx)
          else:
            if y.head < best:
              return argmin_pairs(y.tail, idx + 2, y.head, idx + 1)
            else:
              return argmin_pairs(y.tail, idx + 2, best, best_idx)
