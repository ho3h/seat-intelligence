def prog(xs):
  return second_largest(xs, 0, 0)

def insert_value(value, largest, second):
  if value >= largest:
    return (value, largest)
  else:
    if value > second:
      return (largest, value)
    else:
      return (largest, second)

def second_largest(xs, largest, second):
  match xs:
    case List/Nil:
      return second
    case List/Cons:
      match xs.tail:
        case List/Nil:
          (largest1, second1) = insert_value(xs.head, largest, second)
          return second1
        case List/Cons:
          match xs.tail.tail:
            case List/Nil:
              (largest1, second1) = insert_value(xs.head, largest, second)
              (largest2, second2) = insert_value(xs.tail.head, largest1, second1)
              return second2
            case List/Cons:
              match xs.tail.tail.tail:
                case List/Nil:
                  (largest1, second1) = insert_value(xs.head, largest, second)
                  (largest2, second2) = insert_value(xs.tail.head, largest1, second1)
                  (largest3, second3) = insert_value(xs.tail.tail.head, largest2, second2)
                  return second3
                case List/Cons:
                  (largest1, second1) = insert_value(xs.head, largest, second)
                  (largest2, second2) = insert_value(xs.tail.head, largest1, second1)
                  (largest3, second3) = insert_value(xs.tail.tail.head, largest2, second2)
                  (largest4, second4) = insert_value(xs.tail.tail.tail.head, largest3, second3)
                  return second_largest(xs.tail.tail.tail.tail, largest4, second4)
