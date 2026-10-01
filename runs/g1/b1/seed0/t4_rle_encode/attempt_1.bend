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
      if xs.head == value:
        return rle(xs.tail, value, count + 1)
      else:
        return List/Cons((value, count), rle(xs.tail, xs.head, 1))
