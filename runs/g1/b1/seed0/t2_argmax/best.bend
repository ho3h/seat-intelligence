def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return scan(xs.tail, 1, 0, xs.head)

def scan(xs, i, best_i, best_v):
  match xs:
    case List/Nil:
      return best_i
    case List/Cons:
      ys = xs.tail
      match ys:
        case List/Nil:
          if xs.head > best_v:
            return i
          else:
            return best_i
        case List/Cons:
          if xs.head > best_v:
            if ys.head > xs.head:
              return scan(ys.tail, i + 2, i + 1, ys.head)
            else:
              return scan(ys.tail, i + 2, i, xs.head)
          else:
            if ys.head > best_v:
              return scan(ys.tail, i + 2, i + 1, ys.head)
            else:
              return scan(ys.tail, i + 2, best_i, best_v)
