def prog(x):
  (xs, ys, zs) = x
  return merge3(xs, ys, zs)

def merge3(xs, ys, zs):
  match xs:
    case List/Nil:
      return merge(ys, zs)
    case List/Cons:
      match ys:
        case List/Nil:
          return merge(xs, zs)
        case List/Cons:
          match zs:
            case List/Nil:
              return merge(xs, ys)
            case List/Cons:
              if xs.head <= ys.head:
                if xs.head <= zs.head:
                  return List/Cons(xs.head, merge3(xs.tail, ys, zs))
                else:
                  return List/Cons(zs.head, merge3(xs, ys, zs.tail))
              else:
                if ys.head <= zs.head:
                  return List/Cons(ys.head, merge3(xs, ys.tail, zs))
                else:
                  return List/Cons(zs.head, merge3(xs, ys, zs.tail))

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head <= ys.head:
            return List/Cons(xs.head, merge(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge(xs, ys.tail))
