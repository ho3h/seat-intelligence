def prog(xs):
  return prefix_sums(xs, 0)

def prefix_sums(xs, acc):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      total = acc + xs.head
      return List/Cons(total, prefix_sums(xs.tail, total))
