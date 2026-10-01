def prog(n):
  return range_blocks(0, n)

def range_blocks(i, remaining):
  if remaining >= 64:
    return block16(i, block16(i + 16, block16(i + 32, block16(i + 48, range_blocks(i + 64, remaining - 64)))))
  else:
    if remaining >= 16:
      return block16(i, range_blocks(i + 16, remaining - 16))
    else:
      return range_small(i, remaining)

def block16(i, tail):
  return List/Cons(i, List/Cons(i + 1, List/Cons(i + 2, List/Cons(i + 3, List/Cons(i + 4, List/Cons(i + 5, List/Cons(i + 6, List/Cons(i + 7, List/Cons(i + 8, List/Cons(i + 9, List/Cons(i + 10, List/Cons(i + 11, List/Cons(i + 12, List/Cons(i + 13, List/Cons(i + 14, List/Cons(i + 15, tail))))))))))))))))

def range_small(i, remaining):
  if remaining == 0:
    return []
  else:
    return List/Cons(i, range_small(i + 1, remaining - 1))
