def prog(xs):
  return histogram(xs, 0)

def histogram(xs, v):
  if v == 16:
    return []
  else:
    count = count_value(xs, v, 0)
    rest = histogram(xs, v + 1)
    return List/Cons(count, rest)

def count_value(xs, v, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == v:
        return count_value(xs.tail, v, acc + 1)
      else:
        return count_value(xs.tail, v, acc)
