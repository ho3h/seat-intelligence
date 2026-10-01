def prog(x):
  (a, k) = x
  if k == 0:
    return []
  else:
    return mul_digits(a, k, 0)

def mul_digits(xs, k, carry):
  match xs:
    case List/Nil:
      if carry == 0:
        return []
      else:
        return [carry]
    case List/Cons:
      value = xs.head * k + carry
      digit = value % 4096
      next_carry = value / 4096
      return List/Cons(digit, mul_digits(xs.tail, k, next_carry))
