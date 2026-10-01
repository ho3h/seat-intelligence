def prog(xs):
  return lis_go(xs, [])

def lis_go(xs, ts):
  match xs:
    case List/Nil:
      return lis_len(ts, 0)
    case List/Cons:
      return lis_go(xs.tail, lis_ins(ts, xs.head))

def lis_ins(ts, x):
  match ts:
    case List/Nil:
      return List/Cons(x, List/Nil)
    case List/Cons:
      if ts.head >= x:
        return List/Cons(x, ts.tail)
      else:
        return List/Cons(ts.head, lis_ins(ts.tail, x))

def lis_len(ts, acc):
  match ts:
    case List/Nil:
      return acc
    case List/Cons:
      return lis_len(ts.tail, acc + 1)
