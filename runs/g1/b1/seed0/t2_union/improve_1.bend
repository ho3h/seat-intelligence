def prog(x):
  (xs, ys) = x
  return merge(xs, ys)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head < ys.head:
            return List/Cons(xs.head, merge_left(xs.tail, ys))
          else:
            if xs.head == ys.head:
              return List/Cons(xs.head, merge(xs.tail, ys.tail))
            else:
              return List/Cons(ys.head, merge_right(xs, ys.tail))

def merge_left(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head < ys.head:
            return List/Cons(xs.head, merge_left(xs.tail, ys))
          else:
            if xs.head == ys.head:
              return List/Cons(xs.head, merge_left(xs.tail, ys.tail))
            else:
              return List/Cons(ys.head, merge_right(xs, ys.tail))

def merge_right(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head > ys.head:
            return List/Cons(ys.head, merge_right(xs, ys.tail))
          else:
            if xs.head == ys.head:
              return List/Cons(xs.head, merge_right(xs.tail, ys.tail))
            else:
              return List/Cons(xs.head, merge_left(xs.tail, ys))
