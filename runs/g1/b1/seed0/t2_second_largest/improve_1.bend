def prog(xs):
  return find_second(xs, 0, 0)

def find_second(xs, largest, second):
  match xs:
    case List/Nil:
      return second
    case List/Cons:
      if xs.head > second:
        if xs.head >= largest:
          return find_second(xs.tail, xs.head, largest)
        else:
          return find_second(xs.tail, largest, xs.head)
      else:
        return find_second(xs.tail, largest, second)
