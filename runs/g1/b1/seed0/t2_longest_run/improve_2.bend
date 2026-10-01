def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return scan(xs.tail, xs.head, 1, 0)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def scan(xs, prev, run, best):
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
            if xs.tail.head == prev:
              return scan(xs.tail.tail, prev, next_run + 1, best)
            else:
              return scan(xs.tail.tail, xs.tail.head, 1, max2(next_run, best))
      else:
        next_best = max2(run, best)
        match xs.tail:
          case List/Nil:
            return next_best
          case List/Cons:
            if xs.tail.head == xs.head:
              return scan(xs.tail.tail, xs.head, 2, next_best)
            else:
              return scan(xs.tail.tail, xs.tail.head, 1, next_best)
