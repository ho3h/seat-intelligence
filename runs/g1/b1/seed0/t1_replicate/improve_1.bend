def prog(x):
  (n, v) = x
  return replicate(n, v)

def replicate(n, v):
  if n < 16:
    return replicate_small(n, v)
  else:
    tail = replicate(n - 16, v)
    return List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, List/Cons(v, tail))))))))))))))))

def replicate_small(n, v):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(v, replicate_small(n - 1, v))
