def prog(xs):
  return lis(xs, [])

def lis(xs, tails):
  match xs:
    case List/Nil:
      return length(tails, 0)
    case List/Cons:
      new_tails = place(tails, xs.head)
      return lis(xs.tail, new_tails)

def place(tails, x):
  match tails:
    case List/Nil:
      return [x]
    case List/Cons:
      if x <= tails.head:
        return List/Cons(x, tails.tail)
      else:
        rest = place(tails.tail, x)
        return List/Cons(tails.head, rest)

def length(xs, n):
  match xs:
    case List/Nil:
      return n
    case List/Cons:
      return length(xs.tail, n + 1)
