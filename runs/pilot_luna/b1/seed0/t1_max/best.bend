def prog(xs):
  return max_list(xs, 0)

def max_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head > acc:
        acc1 = xs.head
      else:
        acc1 = acc
      match xs.tail:
        case List/Nil:
          return acc1
        case List/Cons:
          if xs.tail.head > acc1:
            acc2 = xs.tail.head
          else:
            acc2 = acc1
          match xs.tail.tail:
            case List/Nil:
              return acc2
            case List/Cons:
              if xs.tail.tail.head > acc2:
                acc3 = xs.tail.tail.head
              else:
                acc3 = acc2
              match xs.tail.tail.tail:
                case List/Nil:
                  return acc3
                case List/Cons:
                  if xs.tail.tail.tail.head > acc3:
                    acc4 = xs.tail.tail.tail.head
                  else:
                    acc4 = acc3
                  return max_list(xs.tail.tail.tail.tail, acc4)
