def prog(x):
  (a, b) = x
  la = list_len(a)
  lb = list_len(b)
  if la == 0:
    return []
  else:
    if lb == 0:
      return []
    else:
      rb = reverse(b, [])
      count = la + lb - 1
      coeffs = make_diags(a, rb, la, lb, 0, count)
      return trim(normalize(coeffs, 0))

def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def reverse(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse(xs.tail, List/Cons(xs.head, acc))

def drop(xs, n):
  switch n:
    case 0:
      return xs
    case _:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          return drop(xs.tail, n - 1)

def make_diags(a, rb, la, lb, k, remaining):
  if remaining == 0:
    return []
  else:
    if k < lb:
      offset = lb - 1 - k
      aligned_b = drop(rb, offset)
      aligned_a = a
    else:
      offset = k - lb + 1
      aligned_a = drop(a, offset)
      aligned_b = rb
    (digit, carry) = sum_diag(aligned_a, aligned_b, 0, 0)
    tail = make_diags(a, rb, la, lb, k + 1, remaining - 1)
    return List/Cons((digit, carry), tail)

def sum_diag(xs, ys, digit, carry):
  match xs:
    case List/Nil:
      return (digit, carry)
    case List/Cons:
      match ys:
        case List/Nil:
          return (digit, carry)
        case List/Cons:
          total = digit + xs.head * ys.head
          next_digit = total % 4096
          next_carry = carry + total / 4096
          return sum_diag(xs.tail, ys.tail, next_digit, next_carry)

def normalize(coeffs, carry):
  match coeffs:
    case List/Nil:
      return carry_digits(carry)
    case List/Cons:
      (digit, local_carry) = coeffs.head
      total = digit + carry
      out_digit = total % 4096
      next_carry = local_carry + total / 4096
      tail = normalize(coeffs.tail, next_carry)
      return List/Cons(out_digit, tail)

def carry_digits(carry):
  if carry == 0:
    return []
  else:
    digit = carry % 4096
    next_carry = carry / 4096
    return List/Cons(digit, carry_digits(next_carry))

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
