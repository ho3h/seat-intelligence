def prog(xs):
  return min_list(xs, 16777215)

def min_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head < acc:
            return xs.head
          else:
            return acc
        case List/Cons:
          if xs.head < xs.tail.head:
            if xs.head < acc:
              return min_list(xs.tail.tail, xs.head)
            else:
              return min_list(xs.tail.tail, acc)
          else:
            if xs.tail.head < acc:
              return min_list(xs.tail.tail, xs.tail.head)
            else:
              return min_list(xs.tail.tail, acc)
