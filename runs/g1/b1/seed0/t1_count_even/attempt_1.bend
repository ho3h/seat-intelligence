def prog(xs):
  return count_even(xs, 0)

def count_even(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head % 2 == 0:
        return count_even(xs.tail, acc + 1)
      else:
        return count_even(xs.tail, acc)
