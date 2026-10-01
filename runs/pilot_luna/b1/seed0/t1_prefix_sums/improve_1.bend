def prog(xs):
  return scan(xs)

def scan(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return List/Cons(xs.head, List/Nil)
        case List/Cons:
          totals = scan(pair_sums(xs))
          return expand(xs, totals)

def pair_sums(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return List/Cons(xs.head, List/Nil)
        case List/Cons:
          return List/Cons(xs.head + rest.head, pair_sums(rest.tail))

def expand(xs, totals):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return List/Cons(totals.head, List/Nil)
        case List/Cons:
          current = totals.head
          return List/Cons(current - rest.head, List/Cons(current, expand(rest.tail, totals.tail)))
