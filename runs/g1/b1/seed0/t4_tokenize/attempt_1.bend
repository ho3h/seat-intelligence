def prog(xs):
  return parse(xs, 0, 0, [])

def parse(xs, active, num, acc):
  match xs:
    case List/Nil:
      if active == 1:
        return reverse(List/Cons((0, num), acc), [])
      else:
        return reverse(acc, [])
    case List/Cons:
      if xs.head >= 48:
        if xs.head <= 57:
          return parse(xs.tail, 1, num * 10 + xs.head - 48, acc)
        else:
          return finish_char(xs.tail, xs.head, active, num, acc)
      else:
        return finish_char(xs.tail, xs.head, active, num, acc)

def finish_char(tail, c, active, num, acc):
  if active == 1:
    return token_char(tail, c, List/Cons((0, num), acc))
  else:
    return token_char(tail, c, acc)

def token_char(tail, c, acc):
  if c == 32:
    return parse(tail, 0, 0, acc)
  else:
    if c == 40:
      return parse(tail, 0, 0, List/Cons((2, c), acc))
    else:
      if c == 41:
        return parse(tail, 0, 0, List/Cons((2, c), acc))
      else:
        return parse(tail, 0, 0, List/Cons((1, c), acc))

def reverse(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse(xs.tail, List/Cons(xs.head, acc))
