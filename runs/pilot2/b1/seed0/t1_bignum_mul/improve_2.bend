def prog(x):
  (a, b) = x
  aa = trim(a)
  bb = trim(b)
  return mul_big(aa, bb)

def mul_big(a, b):
  la = list_len(a)
  lb = list_len(b)
  if la == 0:
    return []
  else:
    if lb == 0:
      return []
    else:
      if la == 1:
        match a:
          case List/Nil:
            return []
          case List/Cons:
            return trim(scalar_mul(a.head, b, 0))
      else:
        if lb == 1:
          match b:
            case List/Nil:
              return []
            case List/Cons:
              return trim(scalar_mul(b.head, a, 0))
        else:
          n = max_num(la, lb)
          if n <= 2:
            return trim(school_rows(a, b, [], 0))
          else:
            m = n / 2
            (a0, a1) = split_at(a, m)
            (b0, b1) = split_at(b, m)
            if is_empty(a1):
              low = mul_big(a0, b0)
              high = mul_big(a0, b1)
              result = add_big(low, shift_left(high, m))
              return trim(result)
            else:
              if is_empty(b1):
                low = mul_big(a0, b0)
                high = mul_big(a1, b0)
                result = add_big(low, shift_left(high, m))
                return trim(result)
              else:
                z0 = mul_big(a0, b0)
                z2 = mul_big(a1, b1)
                sa = add_big(a0, a1)
                sb = add_big(b0, b1)
                p = mul_big(sa, sb)
                cross0 = sub_big(p, z0)
                cross = sub_big(cross0, z2)
                middle = shift_left(cross, m)
                upper = shift_left(z2, m + m)
                result = add_big(add_big(z0, middle), upper)
                return trim(result)

def max_num(a, b):
  if a < b:
    return b
  else:
    return a

def is_empty(xs):
  match xs:
    case List/Nil:
      return 1
    case List/Cons:
      return 0

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
          (front, back) = split_at(xs.tail, n - 1)
          return (List/Cons(xs.head, front), back)

def shift_left(xs, n):
  switch n:
    case 0:
      return xs
    case _:
      return List/Cons(0, shift_left(xs, n - 1))

def scalar_mul(m, xs, carry):
  match xs:
    case List/Nil:
      if carry == 0:
        return []
      else:
        return List/Cons(carry, [])
    case List/Cons:
      total = m * xs.head + carry
      digit = total % 4096
      next_carry = total / 4096
      return List/Cons(digit, scalar_mul(m, xs.tail, next_carry))

def school_rows(a, b, out, shift):
  match a:
    case List/Nil:
      return out
    case List/Cons:
      row = scalar_mul(a.head, b, 0)
      shifted = shift_left(row, shift)
      next_out = add_big(out, shifted)
      return school_rows(a.tail, b, next_out, shift + 1)

def add_big(x, y):
  match x:
    case List/Nil:
      match y:
        case List/Nil:
          return []
        case List/Cons:
          return add_one_side(y, 0)
    case List/Cons:
      match y:
        case List/Nil:
          return add_one_side(x, 0)
        case List/Cons:
          total = x.head + y.head
          digit = total % 4096
          carry = total / 4096
          tail = add_big_carry(x.tail, y.tail, carry)
          return List/Cons(digit, tail)

def add_big_carry(x, y, carry):
  match x:
    case List/Nil:
      match y:
        case List/Nil:
          if carry == 0:
            return []
          else:
            return List/Cons(carry, [])
        case List/Cons:
          total = y.head + carry
          digit = total % 4096
          next_carry = total / 4096
          tail = add_big_carry([], y.tail, next_carry)
          return List/Cons(digit, tail)
    case List/Cons:
      match y:
        case List/Nil:
          total = x.head + carry
          digit = total % 4096
          next_carry = total / 4096
          tail = add_big_carry(x.tail, [], next_carry)
          return List/Cons(digit, tail)
        case List/Cons:
          total = x.head + y.head + carry
          digit = total % 4096
          next_carry = total / 4096
          tail = add_big_carry(x.tail, y.tail, next_carry)
          return List/Cons(digit, tail)

def add_one_side(xs, carry):
  match xs:
    case List/Nil:
      if carry == 0:
        return []
      else:
        return List/Cons(carry, [])
    case List/Cons:
      total = xs.head + carry
      digit = total % 4096
      next_carry = total / 4096
      tail = add_one_side(xs.tail, next_carry)
      return List/Cons(digit, tail)

def sub_big(x, y):
  return trim(sub_big_borrow(x, y, 0))

def sub_big_borrow(x, y, borrow):
  match x:
    case List/Nil:
      return []
    case List/Cons:
      match y:
        case List/Nil:
          if borrow == 0:
            tail = sub_big_borrow(x.tail, [], 0)
            return List/Cons(x.head, tail)
          else:
            if x.head == 0:
              tail = sub_big_borrow(x.tail, [], 1)
              return List/Cons(4095, tail)
            else:
              tail = sub_big_borrow(x.tail, [], 0)
              return List/Cons(x.head - 1, tail)
        case List/Cons:
          if x.head < y.head + borrow:
            digit = x.head + 4096 - y.head - borrow
            tail = sub_big_borrow(x.tail, y.tail, 1)
            return List/Cons(digit, tail)
          else:
            digit = x.head - y.head - borrow
            tail = sub_big_borrow(x.tail, y.tail, 0)
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
