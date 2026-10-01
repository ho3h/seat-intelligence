def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return argmax(xs.tail, 1, 0, xs.head)

def argmax(xs, idx, best_idx, best_val):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      if xs.head > best_val:
        return argmax(xs.tail, idx + 1, idx, xs.head)
      else:
        return argmax(xs.tail, idx + 1, best_idx, best_val)
