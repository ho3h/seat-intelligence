def prog(xs):
  return distinct_count(xs)

def distinct_count(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      rest = distinct_count(xs.tail)
      if member(xs.head, xs.tail):
        return rest
      else:
        return rest + 1

def member(value, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return member(value, xs.tail)
