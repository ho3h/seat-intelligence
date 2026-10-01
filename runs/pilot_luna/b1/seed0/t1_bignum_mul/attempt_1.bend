def prog(x):
  (a, b) = x
  out = multiply_rows(a, b, 0, [])
  (result, _) = trim(out)
  return result

def multiply_rows(a, b, offset, out):
  match a:
    case List/Nil:
      return out
    case List/Cons:
      next_out = add_at_offset(b, a.head, offset, out)
      return multiply_rows(a.tail, b, offset + 1, next_out)

def add_at_offset(b, digit, offset, out):
  switch offset:
    case 0:
      return multiply_digits(b, digit, out, 0)
    case _:
      match out:
        case List/Nil:
          tail = add_at_offset(b, digit, offset - 1, [])
          return List/Cons(0, tail)
        case List/Cons:
          tail = add_at_offset(b, digit, offset - 1, out.tail)
          return List/Cons(out.head, tail)

def multiply_digits(b, digit, out, carry):
  match b:
    case List/Nil:
      return finish_carry(carry, out)
    case List/Cons:
      return multiply_step(b.head, b.tail, digit, out, carry)

def multiply_step(b_digit, b_tail, digit, out, carry):
  match out:
    case List/Nil:
      value = digit * b_digit + carry
      next_carry = value / 4096
      next_out = multiply_digits(b_tail, digit, [], next_carry)
      return List/Cons(value % 4096, next_out)
    case List/Cons:
      value = digit * b_digit + out.head + carry
      next_carry = value / 4096
      next_out = multiply_digits(b_tail, digit, out.tail, next_carry)
      return List/Cons(value % 4096, next_out)

def finish_carry(carry, out):
  if carry == 0:
    return out
  else:
    match out:
      case List/Nil:
        return List/Cons(carry, [])
      case List/Cons:
        value = out.head + carry
        next_carry = value / 4096
        tail = finish_carry(next_carry, out.tail)
        return List/Cons(value % 4096, tail)

def trim(xs):
  match xs:
    case List/Nil:
      return ([], false)
    case List/Cons:
      (tail, tail_nonzero) = trim(xs.tail)
      if tail_nonzero == true:
        return (List/Cons(xs.head, tail), true)
      else:
        if xs.head == 0:
          return ([], false)
        else:
          return (List/Cons(xs.head, tail), true)
