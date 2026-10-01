def prog(x):
  (a, k) = x
  if k == 0:
    return []
  else:
    return mul_digits(a, k, 0)

def carry_list(c):
  if c == 0:
    return []
  else:
    return [c]

def mul_digits(xs, k, carry):
  match xs:
    case List/Nil:
      return carry_list(carry)
    case List/Cons:
      value1 = xs.head * k + carry
      digit1 = value1 % 4096
      carry1 = value1 / 4096
      rest1 = xs.tail
      match rest1:
        case List/Nil:
          return List/Cons(digit1, carry_list(carry1))
        case List/Cons:
          value2 = rest1.head * k + carry1
          digit2 = value2 % 4096
          carry2 = value2 / 4096
          rest2 = rest1.tail
          match rest2:
            case List/Nil:
              return List/Cons(digit1, List/Cons(digit2, carry_list(carry2)))
            case List/Cons:
              value3 = rest2.head * k + carry2
              digit3 = value3 % 4096
              carry3 = value3 / 4096
              rest3 = rest2.tail
              match rest3:
                case List/Nil:
                  return List/Cons(digit1, List/Cons(digit2, List/Cons(digit3, carry_list(carry3))))
                case List/Cons:
                  value4 = rest3.head * k + carry3
                  digit4 = value4 % 4096
                  carry4 = value4 / 4096
                  return List/Cons(digit1, List/Cons(digit2, List/Cons(digit3, List/Cons(digit4, mul_digits(rest3.tail, k, carry4)))))
