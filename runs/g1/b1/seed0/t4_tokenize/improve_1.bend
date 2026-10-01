def prog(xs):
  return parse(xs)

def parse(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head >= 48:
        if xs.head <= 57:
          (num, rest) = read_digits(xs.tail, xs.head - 48)
          return List/Cons((0, num), parse(rest))
        else:
          return parse_char(xs.tail, xs.head)
      else:
        return parse_char(xs.tail, xs.head)

def read_digits(xs, num):
  match xs:
    case List/Nil:
      return (num, [])
    case List/Cons:
      if xs.head >= 48:
        if xs.head <= 57:
          return read_digits(xs.tail, num * 10 + xs.head - 48)
        else:
          return (num, xs)
      else:
        return (num, xs)

def parse_char(tail, c):
  if c == 32:
    return parse(tail)
  else:
    if c == 40:
      return List/Cons((2, c), parse(tail))
    else:
      if c == 41:
        return List/Cons((2, c), parse(tail))
      else:
        return List/Cons((1, c), parse(tail))
