def prog(x):
  (xs, ys) = x
  return merge(xs, ys)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return dedup(ys)
    case List/Cons:
      match ys:
        case List/Nil:
          return dedup(xs)
        case List/Cons:
          if xs.head < ys.head:
            tail = skip(xs.tail, xs.head)
            return List/Cons(xs.head, merge(tail, ys))
          else:
            if xs.head == ys.head:
              xs_tail = skip(xs.tail, xs.head)
              ys_tail = skip(ys.tail, ys.head)
              return List/Cons(xs.head, merge(xs_tail, ys_tail))
            else:
              tail = skip(ys.tail, ys.head)
              return List/Cons(ys.head, merge(xs, tail))

def dedup(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = skip(xs.tail, xs.head)
      return List/Cons(xs.head, dedup(tail))

def skip(xs, value):
  match xs:
    case List/Nil:
      return xs
    case List/Cons:
      if xs.head == value:
        return skip(xs.tail, value)
      else:
        return xs
