def prog(x):
  (n, pairs) = x
  blocks = n / 24
  if n % 24 == 0:
    count = blocks
  else:
    count = blocks + 1
  words = build_words(pairs, 0, count)
  return n - count_marks(words)

def build_words(pairs, block, count):
  if count == 0:
    return []
  else:
    word = block_mask(pairs, block)
    rest = build_words(pairs, block + 1, count - 1)
    return List/Cons(word, rest)

def block_mask(pairs, block):
  match pairs:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = pairs.head
      mask = endpoint_mask(u, block) | endpoint_mask(v, block)
      return mask | block_mask(pairs.tail, block)

def endpoint_mask(id, block):
  if id / 24 == block:
    return 1 << (id % 24)
  else:
    return 0

def count_marks(words):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      return popcount(words.head) + count_marks(words.tail)

def popcount(x):
  x = x - ((x >> 1) & 5592405)
  x = (x & 3355443) + ((x >> 2) & 3355443)
  x = (x + (x >> 4)) & 986895
  x = x + (x >> 8)
  x = x + (x >> 16)
  return x & 63
