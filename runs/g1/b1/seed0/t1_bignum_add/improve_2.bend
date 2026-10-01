def prog(x):
  (a, b) = x
  packed_a = pack2(a)
  packed_b = pack2(b)
  words = add_blocks(packed_a, packed_b, 0)
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

def take2(xs):
  match xs:
    case List/Nil:
      return (0, 0, ([], 0))
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (xs.head, 0, ([], 1))
        case List/Cons:
          return (xs.head, xs.tail.head, (xs.tail.tail, 2))

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

def add_blocks(a, b, carry):
  (a0, a1, ar) = take2(a)
  (b0, b1, br) = take2(b)
  (arest, na) = ar
  (brest, nb) = br
  if na >= nb:
    n = na
  else:
    n = nb
  if n == 0:
    if carry == 0:
      return []
    else:
      return [carry]
  else:
    (out0, carry1) = word_add(a0, b0, carry)
    if n == 1:
      return List/Cons(out0, add_blocks(arest, brest, carry1))
    else:
      (out1, carry2) = word_add(a1, b1, carry1)
      return List/Cons(out0, List/Cons(out1, add_blocks(arest, brest, carry2)))

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
