def prog(x):
  (a, b) = x
  return add(a, b, 0)

def add(a, b, carry):
  match a:
    case List/Nil:
      match b:
        case List/Nil:
          if carry == 0:
            return []
          else:
            return [carry]
        case List/Cons:
          total = b.head + carry
          digit = total % 4096
          next_carry = total / 4096
          return List/Cons(digit, add([], b.tail, next_carry))
    case List/Cons:
      match b:
        case List/Nil:
          total = a.head + carry
          digit = total % 4096
          next_carry = total / 4096
          return List/Cons(digit, add(a.tail, [], next_carry))
        case List/Cons:
          total = a.head + b.head + carry
          digit = total % 4096
          next_carry = total / 4096
          return List/Cons(digit, add(a.tail, b.tail, next_carry))
