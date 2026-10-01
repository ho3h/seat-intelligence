def prog(xs):
  return second_largest(xs, 0, 0)

def second_largest(xs, largest, second):
  match xs:
    case List/Nil:
      return second
    case List/Cons:
      if xs.head >= largest:
        return second_largest(xs.tail, xs.head, largest)
      else:
        if xs.head > second:
          return second_largest(xs.tail, largest, xs.head)
        else:
          return second_largest(xs.tail, largest, second)
