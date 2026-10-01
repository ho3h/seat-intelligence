def prog(x):
  (a, b) = x
  return norm(mul(a, b))

def hd(l):
  match l:
    case List/Nil:
      return 0
    case List/Cons:
      return l.head

def tl(l):
  match l:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return l.tail

def add_carry(acc, carry):
  if carry == 0:
    return acc
  else:
    match acc:
      case List/Nil:
        return List/Cons(carry, List/Nil)
      case List/Cons:
        s = acc.head + carry
        return List/Cons(s & 4095, add_carry(acc.tail, s >> 12))

def addmul(ai, b, acc, carry):
  match b:
    case List/Nil:
      return add_carry(acc, carry)
    case List/Cons:
      s = hd(acc) + ai * b.head + carry
      return List/Cons(s & 4095, addmul(ai, b.tail, tl(acc), s >> 12))

def mul(a, b):
  match a:
    case List/Nil:
      return List/Nil
    case List/Cons:
      r = mul(a.tail, b)
      return addmul(a.head, b, List/Cons(0, r), 0)

def norm(l):
  match l:
    case List/Nil:
      return List/Nil
    case List/Cons:
      h = l.head
      t = norm(l.tail)
      match t:
        case List/Nil:
          if h == 0:
            return List/Nil
          else:
            return List/Cons(h, List/Nil)
        case List/Cons:
          return List/Cons(h, List/Cons(t.head, t.tail))
