def prog(x):
  (a, b) = x
  return trim(karatsuba(trim(a), trim(b)))

def karatsuba(a, b):
  len_a = list_len(a)
  len_b = list_len(b)
  n = max_num(len_a, len_b)
  if n <= 4:
    return mul_rows(a, b, [], 0)
  else:
    half = n / 2
    (a_low, a_high) = split_at(a, half)
    (b_low, b_high) = split_at(b, half)
    z0 = karatsuba(a_low, b_low)
    z2 = karatsuba(a_high, b_high)
    sum_a = trim(add_lists(a_low, a_high, 0))
    sum_b = trim(add_lists(b_low, b_high, 0))
    sum_product = karatsuba(sum_a, sum_b)
    cross0 = trim(sub_lists(sum_product, z0, 0))
    cross = trim(sub_lists(cross0, z2, 0))
    middle = shift(cross, half)
    high = shift(z2, half * 2)
    return add_lists(add_lists(z0, middle, 0), high, 0)

def max_num(a, b):
  if a < b:
    return b
  else:
    return a

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

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

def sub_lists(x, y, borrow):
  match x:
    case List/Nil:
      match y:
        case List/Nil:
          return []
        case List/Cons:
          need = y.head + borrow
          if need == 0:
            return List/Cons(0, sub_lists([], y.tail, 0))
          else:
            return List/Cons(4096 - need, sub_lists([], y.tail, 1))
    case List/Cons:
      match y:
        case List/Nil:
          if x.head < borrow:
            digit = x.head + 4096 - borrow
            return List/Cons(digit, sub_lists(x.tail, [], 1))
          else:
            digit = x.head - borrow
            return List/Cons(digit, sub_lists(x.tail, [], 0))
        case List/Cons:
          need = y.head + borrow
          if x.head < need:
            digit = x.head + 4096 - need
            return List/Cons(digit, sub_lists(x.tail, y.tail, 1))
          else:
            digit = x.head - need
            return List/Cons(digit, sub_lists(x.tail, y.tail, 0))

def shift(xs, n):
  switch n:
    case 0:
      return xs
    case _:
      return List/Cons(0, shift(xs, n - 1))

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
