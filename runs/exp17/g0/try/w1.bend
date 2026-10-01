def prog(x):
  (n, es) = x
  return (len(es, 0), 0)

def len(xs, a):
  match xs:
    case List/Nil:
      return a
    case List/Cons:
      return len(xs.tail, a + 1)
