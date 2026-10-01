def prog(xs):
  return longest(xs, 0, 0, 0, 0)

def longest(xs, seen, prev, run, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if seen == 0:
        return longest(xs.tail, 1, xs.head, 1, 1)
      else:
        if xs.head == prev:
          next_run = run + 1
          if next_run > best:
            return longest(xs.tail, 1, prev, next_run, next_run)
          else:
            return longest(xs.tail, 1, prev, next_run, best)
        else:
          return longest(xs.tail, 1, xs.head, 1, best)
