def prog(xs):
  return count_distinct(xs, 0)

def contains(xs, v):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == v:
        return 1
      else:
        return contains(xs.tail, v)

def count_distinct(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if contains(xs.tail, xs.head) == 1:
        return count_distinct(xs.tail, acc)
      else:
        return count_distinct(xs.tail, acc + 1)
