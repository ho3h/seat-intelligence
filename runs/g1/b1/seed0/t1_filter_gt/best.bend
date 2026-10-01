def prog(x):
  (k, xs) = x
  return filt2(k, xs)

def filt2(k, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      tail = xs.tail
      match tail:
        case List/Nil:
          if a > k:
            return List/Cons(a, [])
          else:
            return []
        case List/Cons:
          b = tail.head
          rest = filt2(k, tail.tail)
          if a > k:
            if b > k:
              return List/Cons(a, List/Cons(b, rest))
            else:
              return List/Cons(a, rest)
          else:
            if b > k:
              return List/Cons(b, rest)
            else:
              return rest
