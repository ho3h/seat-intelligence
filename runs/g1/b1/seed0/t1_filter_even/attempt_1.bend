def prog(xs):
  return filter_even(xs)

def filter_even(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = filter_even(xs.tail)
      if xs.head % 2 == 0:
        return List/Cons(xs.head, rest)
      else:
        return rest
