def prog(x):
  (a, b) = x
  product = multiply_dc(a, b)
  (result, _) = trim(product)
  return result

def multiply_dc(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      if a.tail == []:
        return multiply_row(b, a.head, 0)
      else:
        size = length(a)
        left_size = size / 2
        (left, right) = split_at(a, left_size)
        left_product = multiply_dc(left, b)
        right_product = multiply_dc(right, b)
        shifted_right = shift(right_product, left_size)
        return add_lists(left_product, shifted_right, 0)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def split_at(xs, count):
  switch count:
    case 0:
      return ([], xs)
    case _:
      match xs:
        case List/Nil:
          return ([], [])
        case List/Cons:
          (left, right) = split_at(xs.tail, count - 1)
          return (List/Cons(xs.head, left), right)

def multiply_row(b, digit, carry):
  match b:
    case List/Nil:
      return finish_carry(carry, [])
    case List/Cons:
      value = digit * b.head + carry
      next_carry = value / 4096
      rest = multiply_row(b.tail, digit, next_carry)
      return List/Cons(value % 4096, rest)

def shift(xs, count):
  switch count:
    case 0:
      return xs
    case _:
      return List/Cons(0, shift(xs, count - 1))

def add_lists(a, b, carry):
  match a:
    case List/Nil:
      match b:
        case List/Nil:
          return finish_carry(carry, [])
        case List/Cons:
          value = b.head + carry
          rest = add_lists([], b.tail, value / 4096)
          return List/Cons(value % 4096, rest)
    case List/Cons:
      match b:
        case List/Nil:
          value = a.head + carry
          rest = add_lists(a.tail, [], value / 4096)
          return List/Cons(value % 4096, rest)
        case List/Cons:
          value = a.head + b.head + carry
          rest = add_lists(a.tail, b.tail, value / 4096)
          return List/Cons(value % 4096, rest)

def finish_carry(carry, out):
  if carry == 0:
    return out
  else:
    value = carry % 4096
    next_carry = carry / 4096
    return List/Cons(value, finish_carry(next_carry, out))

def trim(xs):
  match xs:
    case List/Nil:
      return ([], 0)
    case List/Cons:
      (tail, tail_nonzero) = trim(xs.tail)
      if tail_nonzero == 1:
        return (List/Cons(xs.head, tail), 1)
      else:
        if xs.head == 0:
          return ([], 0)
        else:
          return (List/Cons(xs.head, tail), 1)
