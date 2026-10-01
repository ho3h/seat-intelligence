def prog(xs):
  n = length(xs)
  sorted = sort(xs)
  return nth(sorted, n / 2)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      sorted_tail = sort(xs.tail)
      return insert(xs.head, sorted_tail)

def insert(x, xs):
  match xs:
    case List/Nil:
      return List/Cons(x, [])
    case List/Cons:
      if x <= xs.head:
        return List/Cons(x, xs)
      else:
        rest = insert(x, xs.tail)
        return List/Cons(xs.head, rest)

def nth(xs, k):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if k == 0:
        return xs.head
      else:
        return nth(xs.tail, k - 1)
