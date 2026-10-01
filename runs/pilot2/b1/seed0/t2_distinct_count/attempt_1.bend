def prog(xs):
  return count_unique(xs, [], 0)

def count_unique(xs, seen, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if contains(seen, xs.head) == 1:
        return count_unique(xs.tail, seen, acc)
      else:
        return count_unique(xs.tail, List/Cons(xs.head, seen), acc + 1)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)
