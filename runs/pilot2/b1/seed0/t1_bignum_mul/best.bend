def prog(x):
  (a, b) = x
  result = mul_rows(a, b, [], 0)
  return trim(result)

def mul_rows(a, b, out, shift):
  match a:
    case List/Nil:
      return out
    case List/Cons:
      next_out = add_shift(a.head, b, out, shift)
      return mul_rows(a.tail, b, next_out, shift + 1)

def add_shift(m, b, out, shift):
  switch shift:
    case 0:
      return mul_row(m, b, out, 0)
    case _:
      match out:
        case List/Nil:
          tail = add_shift(m, b, [], shift - 1)
          return List/Cons(0, tail)
        case List/Cons:
          tail = add_shift(m, b, out.tail, shift - 1)
          return List/Cons(out.head, tail)

def mul_row(m, b, out, carry):
  match b:
    case List/Nil:
      return add_carry(carry, out)
    case List/Cons:
      match out:
        case List/Nil:
          total = m * b.head + carry
          digit = total % 4096
          next_carry = total / 4096
          tail = mul_row(m, b.tail, [], next_carry)
          return List/Cons(digit, tail)
        case List/Cons:
          total = out.head + m * b.head + carry
          digit = total % 4096
          next_carry = total / 4096
          tail = mul_row(m, b.tail, out.tail, next_carry)
          return List/Cons(digit, tail)

def add_carry(carry, out):
  if carry == 0:
    return out
  else:
    match out:
      case List/Nil:
        return List/Cons(carry, [])
      case List/Cons:
        total = out.head + carry
        digit = total % 4096
        next_carry = total / 4096
        tail = add_carry(next_carry, out.tail)
        return List/Cons(digit, tail)

def trim(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = trim(xs.tail)
      match tail:
        case List/Nil:
          if xs.head == 0:
            return []
          else:
            return List/Cons(xs.head, [])
        case List/Cons:
          return List/Cons(xs.head, tail)
