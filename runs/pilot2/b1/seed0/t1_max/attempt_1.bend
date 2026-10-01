def prog(xs):
  return max_list(xs, 0)

def max_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head > acc:
        return max_list(xs.tail, xs.head)
      else:
        return max_list(xs.tail, acc)
