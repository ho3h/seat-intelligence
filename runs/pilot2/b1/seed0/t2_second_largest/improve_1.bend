def prog(xs):
  return second_largest(xs, 0, 0)

def second_largest(xs, largest, second):
  match xs:
    case List/Nil:
      return second
    case List/Cons:
      match xs.tail:
        case List/Nil:
          if xs.head >= largest:
            return largest
          else:
            if xs.head > second:
              return xs.head
            else:
              return second
        case List/Cons:
          if xs.head >= largest:
            if xs.tail.head >= xs.head:
              return second_largest(xs.tail.tail, xs.tail.head, xs.head)
            else:
              if xs.tail.head >= largest:
                return second_largest(xs.tail.tail, xs.head, xs.tail.head)
              else:
                return second_largest(xs.tail.tail, xs.head, largest)
          else:
            if xs.head > second:
              if xs.tail.head >= largest:
                return second_largest(xs.tail.tail, xs.tail.head, largest)
              else:
                if xs.tail.head > xs.head:
                  return second_largest(xs.tail.tail, largest, xs.tail.head)
                else:
                  return second_largest(xs.tail.tail, largest, xs.head)
            else:
              if xs.tail.head >= largest:
                return second_largest(xs.tail.tail, xs.tail.head, largest)
              else:
                if xs.tail.head > second:
                  return second_largest(xs.tail.tail, largest, xs.tail.head)
                else:
                  return second_largest(xs.tail.tail, largest, second)
