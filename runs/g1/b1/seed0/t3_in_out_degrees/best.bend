def prog(x):
  (n, edges) = x
  ins = zeros(n)
  outs = zeros(n)
  return degrees(edges, ins, outs)

def zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, zeros(n - 1))

def inc(xs, i):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(xs.head + 1, xs.tail)
      else:
        return List/Cons(xs.head, inc(xs.tail, i - 1))

def degrees(edges, ins, outs):
  match edges:
    case List/Nil:
      return (ins, outs)
    case List/Cons:
      (u, v) = edges.head
      ins2 = inc(ins, v)
      outs2 = inc(outs, u)
      return degrees(edges.tail, ins2, outs2)
