def prog(x):
  (xs, ys) = x
  return merge_first(xs, ys)

def merge_first(xs, ys):
  match xs:
    case List/Nil:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(ys.head, merge_rest(xs, ys.tail, ys.head))
    case List/Cons:
      match ys:
        case List/Nil:
          return List/Cons(xs.head, merge_rest(xs.tail, ys, xs.head))
        case List/Cons:
          if xs.head < ys.head:
            return List/Cons(xs.head, merge_rest(xs.tail, ys, xs.head))
          else:
            if xs.head > ys.head:
              return List/Cons(ys.head, merge_rest(xs, ys.tail, ys.head))
            else:
              return List/Cons(xs.head, merge_rest(xs.tail, ys.tail, xs.head))

def merge_rest(xs, ys, prev):
  match xs:
    case List/Nil:
      match ys:
        case List/Nil:
          return []
        case List/Cons:
          if ys.head == prev:
            return merge_rest(xs, ys.tail, prev)
          else:
            return List/Cons(ys.head, merge_rest(xs, ys.tail, ys.head))
    case List/Cons:
      match ys:
        case List/Nil:
          if xs.head == prev:
            return merge_rest(xs.tail, ys, prev)
          else:
            return List/Cons(xs.head, merge_rest(xs.tail, ys, xs.head))
        case List/Cons:
          if xs.head < ys.head:
            if xs.head == prev:
              return merge_rest(xs.tail, ys, prev)
            else:
              return List/Cons(xs.head, merge_rest(xs.tail, ys, xs.head))
          else:
            if xs.head > ys.head:
              if ys.head == prev:
                return merge_rest(xs, ys.tail, prev)
              else:
                return List/Cons(ys.head, merge_rest(xs, ys.tail, ys.head))
            else:
              if xs.head == prev:
                return merge_rest(xs.tail, ys.tail, prev)
              else:
                return List/Cons(xs.head, merge_rest(xs.tail, ys.tail, xs.head))
