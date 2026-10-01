def prog(xs):
  return radix_count(xs, 22)

def radix_count(xs, shift):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b, c, d) = split4(xs, shift, [], [], [], [])
      if shift == 0:
        return nonempty(a) + nonempty(b) + nonempty(c) + nonempty(d)
      else:
        return radix_count(a, shift - 2) + radix_count(b, shift - 2) + radix_count(c, shift - 2) + radix_count(d, shift - 2)

def split4(xs, shift, a, b, c, d):
  match xs:
    case List/Nil:
      return (a, b, c, d)
    case List/Cons:
      bucket = (xs.head >> shift) & 3
      if bucket == 0:
        return split4(xs.tail, shift, List/Cons(xs.head, a), b, c, d)
      else:
        if bucket == 1:
          return split4(xs.tail, shift, a, List/Cons(xs.head, b), c, d)
        else:
          if bucket == 2:
            return split4(xs.tail, shift, a, b, List/Cons(xs.head, c), d)
          else:
            return split4(xs.tail, shift, a, b, c, List/Cons(xs.head, d))

def nonempty(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1
