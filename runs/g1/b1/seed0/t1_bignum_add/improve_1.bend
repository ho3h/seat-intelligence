def prog(x):
  (a, b) = x
  packed_a = pack2(a)
  packed_b = pack2(b)
  words = add_words(packed_a, packed_b, 0)
  return unpack(words)

def pack2(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      low = xs.head
      match xs.tail:
        case List/Nil:
          return [low]
        case List/Cons:
          word = low + xs.tail.head * 4096
          return List/Cons(word, pack2(xs.tail.tail))

def word_add(u, v, carry):
  total = u + v + carry
  threshold = 16777215 - v
  if carry == 0:
    if u > threshold:
      return (total, 1)
    else:
      return (total, 0)
  else:
    if u >= threshold:
      return (total, 1)
    else:
      return (total, 0)

def add_words(a, b, carry):
  match a:
    case List/Nil:
      match b:
        case List/Nil:
          if carry == 0:
            return []
          else:
            return [carry]
        case List/Cons:
          (total, next_carry) = word_add(0, b.head, carry)
          return List/Cons(total, add_words([], b.tail, next_carry))
    case List/Cons:
      match b:
        case List/Nil:
          (total, next_carry) = word_add(a.head, 0, carry)
          return List/Cons(total, add_words(a.tail, [], next_carry))
        case List/Cons:
          (total, next_carry) = word_add(a.head, b.head, carry)
          return List/Cons(total, add_words(a.tail, b.tail, next_carry))

def unpack(words):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      low = words.head % 4096
      high = words.head / 4096
      match words.tail:
        case List/Nil:
          if high == 0:
            return [low]
          else:
            return [low, high]
        case List/Cons:
          return List/Cons(low, List/Cons(high, unpack(words.tail)))
