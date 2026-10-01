def prog(xs):
  return scan4(xs, 0, 0, 0)

def scan4(xs, index, best, best_index):
  match xs:
    case List/Nil:
      return best_index
    case List/Cons:
      if xs.head > best:
        best1 = xs.head
        best_index1 = index
      else:
        best1 = best
        best_index1 = best_index
      match xs.tail:
        case List/Nil:
          return best_index1
        case List/Cons:
          if xs.tail.head > best1:
            best2 = xs.tail.head
            best_index2 = index + 1
          else:
            best2 = best1
            best_index2 = best_index1
          match xs.tail.tail:
            case List/Nil:
              return best_index2
            case List/Cons:
              if xs.tail.tail.head > best2:
                best3 = xs.tail.tail.head
                best_index3 = index + 2
              else:
                best3 = best2
                best_index3 = best_index2
              match xs.tail.tail.tail:
                case List/Nil:
                  return best_index3
                case List/Cons:
                  if xs.tail.tail.tail.head > best3:
                    best4 = xs.tail.tail.tail.head
                    best_index4 = index + 3
                  else:
                    best4 = best3
                    best_index4 = best_index3
                  return scan4(xs.tail.tail.tail.tail, index + 4, best4, best_index4)
