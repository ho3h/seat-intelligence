def prog(x):
  (xs, t) = x
  return search4(xs, t, 0)

def search4(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return linear(xs, t, i)
        case List/Cons:
          match xs.tail.tail:
            case List/Nil:
              return linear(xs, t, i)
            case List/Cons:
              match xs.tail.tail.tail:
                case List/Nil:
                  return linear(xs, t, i)
                case List/Cons:
                  if xs.tail.tail.tail.head == t:
                    return i + 3
                  else:
                    if xs.tail.tail.tail.head < t:
                      return search4(xs.tail.tail.tail.tail, t, i + 4)
                    else:
                      return scan3(xs.head, xs.tail.head, xs.tail.tail.head, t, i)

def scan3(a, b, c, t, i):
  if a == t:
    return i
  else:
    if a > t:
      return 16777215
    else:
      if b == t:
        return i + 1
      else:
        if b > t:
          return 16777215
        else:
          if c == t:
            return i + 2
          else:
            return 16777215

def linear(xs, t, i):
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
          return linear(xs.tail, t, i + 1)
