def prog(x):
  (n, es) = x
  return (len(es, 0), 0)

def len(xs, a):
  fold xs with a:
    case List/Nil:
      return a
    case List/Cons:
      return xs.tail(a + 1)
