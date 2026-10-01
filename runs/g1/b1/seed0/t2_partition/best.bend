def prog(x):
  (p, xs) = x
  return partition(xs, p)

def partition(xs, p):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      ys = xs.tail
      match ys:
        case List/Nil:
          if xs.head < p:
            return ([xs.head], [])
          else:
            return ([], [xs.head])
        case List/Cons:
          (lo, hi) = partition(ys.tail, p)
          if xs.head < p:
            if ys.head < p:
              return (List/Cons(xs.head, List/Cons(ys.head, lo)), hi)
            else:
              return (List/Cons(xs.head, lo), List/Cons(ys.head, hi))
          else:
            if ys.head < p:
              return (List/Cons(ys.head, lo), List/Cons(xs.head, hi))
            else:
              return (lo, List/Cons(xs.head, List/Cons(ys.head, hi)))
