def prog(x):
  (a, b) = x
  return mul_rows(a, b, [], 0)

def mul_rows(a, b, acc, pos):
  match a:
    case List/Nil:
      return trim(acc)
    case List/Cons:
      product = mul_digit(b, a.head, 0)
      shifted = concat(zeros(pos), product)
      next_acc = add_lists(acc, shifted, 0)
      return mul_rows(a.tail, b, next_acc, pos + 1)

def mul_digit(xs, digit, carry):
  match xs:
    case List/Nil:
      if carry == 0:
        return []
      else:
        return List/Cons(carry, [])
    case List/Cons:
      value = xs.head * digit + carry
      out_digit = value % 4096
      next_carry = value / 4096
      return List/Cons(out_digit, mul_digit(xs.tail, digit, next_carry))

def add_lists(x, y, carry):
  match x:
    case List/Nil:
      match y:
        case List/Nil:
          if carry == 0:
            return []
          else:
            return List/Cons(carry, [])
        case List/Cons:
          value = y.head + carry
          out_digit = value % 4096
          next_carry = value / 4096
          return List/Cons(out_digit, add_lists([], y.tail, next_carry))
    case List/Cons:
      match y:
        case List/Nil:
          value = x.head + carry
          out_digit = value % 4096
          next_carry = value / 4096
          return List/Cons(out_digit, add_lists(x.tail, [], next_carry))
        case List/Cons:
          value = x.head + y.head + carry
          out_digit = value % 4096
          next_carry = value / 4096
          return List/Cons(out_digit, add_lists(x.tail, y.tail, next_carry))

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, concat(xs.tail, ys))

def zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, zeros(n - 1))

def trim(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = trim(xs.tail)
      match rest:
        case List/Nil:
          if xs.head == 0:
            return []
          else:
            return List/Cons(xs.head, [])
        case List/Cons:
          return List/Cons(xs.head, rest)
