def prog(x):
  (c, mnl) = x
  return count_conflicts(c, mnl, 0)

def count_conflicts(c, pairs, acc):
  match pairs:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = pairs.head
      if get_at(c, a) == get_at(c, b):
        return count_conflicts(c, pairs.tail, acc + 1)
      else:
        return count_conflicts(c, pairs.tail, acc)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)
