def prog(x):
  return prefix(x, 0)

def prefix(xs, acc):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      total = acc + xs.head
      return List/Cons(total, prefix(xs.tail, total))
