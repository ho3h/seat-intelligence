def prog(xs):
  return lis(xs, [])

def lis(xs, tails):
  match xs:
    case List/Nil:
      return length(tails)
    case List/Cons:
      next_tails = place(tails, xs.head)
      return lis(xs.tail, next_tails)

def place(tails, x):
  match tails:
    case List/Nil:
      return List/Cons(x, List/Nil)
    case List/Cons:
      if x <= tails.head:
        return List/Cons(x, tails.tail)
      else:
        next_tail = place(tails.tail, x)
        return List/Cons(tails.head, next_tail)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)
