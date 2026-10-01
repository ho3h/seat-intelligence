def prog(x):
  (k, xs) = x
  s = msort(xs)
  return take(k, s)

def take(k, xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if k == 0:
        return List/Nil
      else:
        return List/Cons(xs.head, take(k - 1, xs.tail))

def split(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (a, b) = split(xs.tail)
      return (List/Cons(xs.head, b), a)

def msort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      h = xs.head
      t = xs.tail
      match t:
        case List/Nil:
          return List/Cons(h, List/Nil)
        case List/Cons:
          (a, b) = split(List/Cons(h, List/Cons(t.head, t.tail)))
          return merge(msort(a), msort(b))

def merge(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return List/Cons(a.head, a.tail)
        case List/Cons:
          if a.head >= b.head:
            return List/Cons(a.head, merge(a.tail, List/Cons(b.head, b.tail)))
          else:
            return List/Cons(b.head, merge(List/Cons(a.head, a.tail), b.tail))
