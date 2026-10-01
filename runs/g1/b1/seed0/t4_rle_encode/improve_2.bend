def prog(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      return rle(xs.tail, xs.head, 1)

def step(item, value, count):
  if item == value:
    return ([], value, count + 1)
  else:
    return ([(value, count)], item, 1)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def small(xs, value, count):
  match xs:
    case List/Nil:
      return [(value, count)]
    case List/Cons:
      (out, next_value, next_count) = step(xs.head, value, count)
      return append(out, small(xs.tail, next_value, next_count))

def block4(a, b, c, d, rest, value, count):
  (out1, value1, count1) = step(a, value, count)
  (out2, value2, count2) = step(b, value1, count1)
  (out3, value3, count3) = step(c, value2, count2)
  (out4, value4, count4) = step(d, value3, count3)
  tail = rle(rest, value4, count4)
  return append(out1, append(out2, append(out3, append(out4, tail))))

def rle(xs, value, count):
  match xs:
    case List/Nil:
      return [(value, count)]
    case List/Cons:
      a = xs.tail
      match a:
        case List/Nil:
          return small(xs, value, count)
        case List/Cons:
          b = a.tail
          match b:
            case List/Nil:
              return small(xs, value, count)
            case List/Cons:
              c = b.tail
              match c:
                case List/Nil:
                  return small(xs, value, count)
                case List/Cons:
                  return block4(xs.head, a.head, b.head, c.head, c.tail, value, count)
