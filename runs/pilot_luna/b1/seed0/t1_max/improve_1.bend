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
          return max_list(xs.tail.tail, acc2)
