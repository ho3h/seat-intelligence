def prog(xs):
  return min_list(xs, 16777215)

def min_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head < acc:
        return min_list(xs.tail, xs.head)
      else:
        return min_list(xs.tail, acc)
