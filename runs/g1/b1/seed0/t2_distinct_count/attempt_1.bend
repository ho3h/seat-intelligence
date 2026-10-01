def prog(xs):
  return distinct_count(xs)

def distinct_count(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      rest = distinct_count(xs.tail)
      if contains(xs.tail, xs.head) == 1:
        return rest
      else:
        return rest + 1

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)
