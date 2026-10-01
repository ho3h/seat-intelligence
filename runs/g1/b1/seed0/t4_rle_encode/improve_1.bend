def prog(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return rle(xs.tail, xs.head, 1)

def rle(xs, value, count):
  match xs:
    case List/Nil:
      return List/Cons((value, count), List/Nil)
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          if xs.head == value:
            return List/Cons((value, count + 1), List/Nil)
          else:
            return List/Cons((value, count), List/Cons((xs.head, 1), List/Nil))
        case List/Cons:
          if xs.head == value:
            if rest.head == value:
              return rle(rest.tail, value, count + 2)
            else:
              return List/Cons((value, count + 1), rle(rest.tail, rest.head, 1))
          else:
            if rest.head == xs.head:
              return List/Cons((value, count), rle(rest.tail, xs.head, 2))
            else:
              return List/Cons((value, count), List/Cons((xs.head, 1), rle(rest.tail, rest.head, 1)))
