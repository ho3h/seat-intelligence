def prog(xs):
  return sum_list(xs, 0)

def sum_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return sum_list(xs.tail, acc + xs.head)
