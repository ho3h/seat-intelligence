def prog(xs):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      return check_sorted(xs.tail, xs.head)

def check_sorted(xs, prev):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      if xs.head < prev:
        return 0
      else:
        return check_sorted(xs.tail, xs.head)
