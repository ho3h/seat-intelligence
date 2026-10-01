def prog(x):
  (n, es) = x
  return (len(es), 0)

def len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + len(xs.tail)
