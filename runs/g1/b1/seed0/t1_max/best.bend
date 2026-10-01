def prog(xs):
  return max_acc(xs, 0)

def max_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head > acc:
        return max_acc(xs.tail, xs.head)
      else:
        return max_acc(xs.tail, acc)
