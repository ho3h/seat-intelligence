def prog(x):
  (n, es) = x
  return (len(es, 0), 0)

def len(es, a):
  match es:
    case List/Nil:
      return a
    case List/Cons:
      return len(es.tail, a + 1)
