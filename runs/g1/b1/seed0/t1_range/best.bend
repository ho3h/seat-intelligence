def prog(n):
  return build(0, n)

def build(i, n):
  if n - i >= 32:
    tail = build(i + 32, n)
    return List/Cons(i, List/Cons(i + 1, List/Cons(i + 2, List/Cons(i + 3, List/Cons(i + 4, List/Cons(i + 5, List/Cons(i + 6, List/Cons(i + 7, List/Cons(i + 8, List/Cons(i + 9, List/Cons(i + 10, List/Cons(i + 11, List/Cons(i + 12, List/Cons(i + 13, List/Cons(i + 14, List/Cons(i + 15, List/Cons(i + 16, List/Cons(i + 17, List/Cons(i + 18, List/Cons(i + 19, List/Cons(i + 20, List/Cons(i + 21, List/Cons(i + 22, List/Cons(i + 23, List/Cons(i + 24, List/Cons(i + 25, List/Cons(i + 26, List/Cons(i + 27, List/Cons(i + 28, List/Cons(i + 29, List/Cons(i + 30, List/Cons(i + 31, tail))))))))))))))))))))))))))))))))
  else:
    if i == n:
      return []
    else:
      return List/Cons(i, build(i + 1, n))
