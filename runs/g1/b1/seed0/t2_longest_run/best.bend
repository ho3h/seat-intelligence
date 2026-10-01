def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return pairs(xs.tail, xs.head, 1, 0)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def pairs(xs, prev, run, best):
  match xs:
    case List/Nil:
      return max2(run, best)
    case List/Cons:
      if xs.head == prev:
        next_run = run + 1
        match xs.tail:
          case List/Nil:
            return max2(next_run, best)
          case List/Cons:
            if xs.tail.head == xs.head:
              return pairs(xs.tail.tail, xs.head, next_run + 1, best)
            else:
              next_best = max2(next_run, best)
              return pairs(xs.tail.tail, xs.tail.head, 1, next_best)
      else:
        next_best = max2(run, best)
        match xs.tail:
          case List/Nil:
            return next_best
          case List/Cons:
            if xs.tail.head == xs.head:
              return pairs(xs.tail.tail, xs.head, 2, next_best)
            else:
              return pairs(xs.tail.tail, xs.tail.head, 1, next_best)
