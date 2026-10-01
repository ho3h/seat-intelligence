def prog(xs):
  return find_second(xs, 0, 0)

def pair_step(x, y, largest, second):
  if x >= y:
    if x >= largest:
      if y > largest:
        return (x, y)
      else:
        return (x, largest)
    else:
      if x > second:
        return (largest, x)
      else:
        return (largest, second)
  else:
    if y >= largest:
      if x > largest:
        return (y, x)
      else:
        return (y, largest)
    else:
      if y > second:
        return (largest, y)
      else:
        return (largest, second)

def find_second(xs, largest, second):
  match xs:
    case List/Nil:
      return second
    case List/Cons:
      match xs.tail:
        case List/Nil:
          (new_largest, new_second) = pair_step(xs.head, 0, largest, second)
          return new_second
        case List/Cons:
          (new_largest, new_second) = pair_step(xs.head, xs.tail.head, largest, second)
          return find_second(xs.tail.tail, new_largest, new_second)
