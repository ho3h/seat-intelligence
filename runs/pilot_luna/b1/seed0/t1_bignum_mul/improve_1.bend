def prog(x):
  (a, b) = x
  na = length(a)
  nb = length(b)
  width = na + nb
  rows = make_rows(a, b, 0, width)
  digits = normalize_columns(rows, width, na, 0)
  (result, _) = trim(digits)
  return result

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def make_rows(a, b, offset, width):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      row = multiply_row(b, a.head, 0)
      padded = shift_and_pad(row, offset, width)
      rest = make_rows(a.tail, b, offset + 1, width)
      return List/Cons(padded, rest)

def multiply_row(b, digit, carry):
  match b:
    case List/Nil:
      if carry == 0:
        return []
      else:
        return List/Cons(carry, [])
    case List/Cons:
      value = digit * b.head + carry
      next_carry = value / 4096
      tail = multiply_row(b.tail, digit, next_carry)
      return List/Cons(value % 4096, tail)

def shift_and_pad(row, offset, width):
  zeros = zeroes(offset)
  padded = pad_to(row, width - offset)
  return append(zeros, padded)

def zeroes(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, zeroes(n - 1))

def pad_to(xs, n):
  switch n:
    case 0:
      return []
    case _:
      match xs:
        case List/Nil:
          return List/Cons(0, zeroes(n - 1))
        case List/Cons:
          return List/Cons(xs.head, pad_to(xs.tail, n - 1))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def normalize_columns(rows, width, row_count, carry):
  switch width:
    case 0:
      return finish_carry(carry, [])
    case _:
      (column_sum, tails) = sum_heads(rows, row_count)
      value = column_sum + carry
      digit = value % 4096
      next_carry = value / 4096
      rest = normalize_columns(tails, width - 1, row_count, next_carry)
      return List/Cons(digit, rest)

def sum_heads(rows, count):
  switch count:
    case 0:
      return (0, [])
    case 1:
      match rows:
        case List/Nil:
          return (0, [])
        case List/Cons:
          match rows.head:
            case List/Nil:
              return (0, List/Cons([], []))
            case List/Cons:
              return (rows.head.head, List/Cons(rows.head.tail, []))
    case _:
      left_count = count / 2
      right_count = count - left_count
      (left_rows, right_rows) = split_rows(rows, left_count)
      (left_sum, left_tails) = sum_heads(left_rows, left_count)
      (right_sum, right_tails) = sum_heads(right_rows, right_count)
      return (left_sum + right_sum, append(left_tails, right_tails))

def split_rows(rows, count):
  switch count:
    case 0:
      return ([], rows)
    case _:
      match rows:
        case List/Nil:
          return ([], [])
        case List/Cons:
          (left, right) = split_rows(rows.tail, count - 1)
          return (List/Cons(rows.head, left), right)

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
