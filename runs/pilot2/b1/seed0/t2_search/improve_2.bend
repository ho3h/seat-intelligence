def prog(x):
  (xs, t) = x
  return search_blocks(xs, t, 0)

def search_blocks(xs, t, i):
  (ok, last, rest) = take_block(xs, 32)
  if ok == 0:
    return linear_search(xs, t, i)
  else:
    if last < t:
      return search_blocks(rest, t, i + 32)
    else:
      return linear_search(xs, t, i)

def take_block(xs, n):
  match xs:
    case List/Nil:
      return (0, 0, [])
    case List/Cons:
      if n == 1:
        return (1, xs.head, xs.tail)
      else:
        return take_block(xs.tail, n - 1)

def linear_search(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if xs.head == t:
        return i
      else:
        if xs.head > t:
          return 16777215
        else:
          return linear_search(xs.tail, t, i + 1)
