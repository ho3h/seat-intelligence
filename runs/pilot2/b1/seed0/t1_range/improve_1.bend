def prog(n):
  return range_blocks(0, n)

def range_blocks(i, remaining):
  if remaining >= 16:
    return List/Cons(i, List/Cons(i + 1, List/Cons(i + 2, List/Cons(i + 3, List/Cons(i + 4, List/Cons(i + 5, List/Cons(i + 6, List/Cons(i + 7, List/Cons(i + 8, List/Cons(i + 9, List/Cons(i + 10, List/Cons(i + 11, List/Cons(i + 12, List/Cons(i + 13, List/Cons(i + 14, List/Cons(i + 15, range_blocks(i + 16, remaining - 16))))))))))))))))
  else:
    return range_small(i, remaining)

def range_small(i, remaining):
  if remaining == 0:
    return []
  else:
    return List/Cons(i, range_small(i + 1, remaining - 1))
