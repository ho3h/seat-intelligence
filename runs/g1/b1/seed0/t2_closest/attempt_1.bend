def prog(input):
  (x, xs) = input
  return closest(xs, x, 0, 0)

def closest(xs, x, best, seen):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if seen == 0:
        return closest(xs.tail, x, xs.head, 1)
      else:
        d_head = absdiff(xs.head, x)
        d_best = absdiff(best, x)
        if d_head < d_best:
          return closest(xs.tail, x, xs.head, 1)
        else:
          if d_head == d_best:
            if xs.head < best:
              return closest(xs.tail, x, xs.head, 1)
            else:
              return closest(xs.tail, x, best, 1)
          else:
            return closest(xs.tail, x, best, 1)

def absdiff(a, b):
  if a >= b:
    return a - b
  else:
    return b - a
