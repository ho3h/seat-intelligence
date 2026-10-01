def prog(x):
  (a, b) = x
  len_a = list_len(a)
  len_b = list_len(b)
  if len_a < len_b:
    return trim(mul_tree(b, a, len_b))
  else:
    return trim(mul_tree(a, b, len_a))

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def mul_tree(a, b, n):
  switch n:
    case 0:
      return []
    case 1:
      match a:
        case List/Nil:
          return []
        case List/Cons:
          return mul_digit(b, a.head, 0)
    case _:
      half = n / 2
      (low, high) = split_at(a, half)
      low_product = mul_tree(low, b, half)
      high_product = mul_tree(high, b, n - half)
      shifted_high = shift(high_product, half)
      return add_lists(low_product, shifted_high, 0)

def split_at(xs, n):
  switch n:
    case 0:
      return ([], xs)
    case _:
      match xs:
        case List/Nil:
          return ([], [])
        case List/Cons:
          (prefix, suffix) = split_at(xs.tail, n - 1)
          return (List/Cons(xs.head, prefix), suffix)

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

def shift(xs, n):
  switch n:
    case 0:
      return xs
    case _:
      return List/Cons(0, shift(xs, n - 1))

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
