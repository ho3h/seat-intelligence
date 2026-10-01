def prog(x):
  (n, pairs) = x
  blocks = n / 24
  if n % 24 == 0:
    words = make_words(blocks)
  else:
    words = make_words(blocks + 1)
  marked_words = mark_edges(pairs, words)
  marked = count_marked(marked_words, n)
  return n - marked

def make_words(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, make_words(count - 1))

def mark_edges(pairs, words):
  match pairs:
    case List/Nil:
      return words
    case List/Cons:
      (u, v) = pairs.head
      updated = mark_pair(words, u, v)
      return mark_edges(pairs.tail, updated)

def mark_pair(words, u, v):
  u_block = u / 24
  v_block = v / 24
  u_mask = 1 << (u % 24)
  v_mask = 1 << (v % 24)
  if u_block == v_block:
    return set_word(words, u_block, u_mask | v_mask)
  else:
    updated = set_word(words, u_block, u_mask)
    return set_word(updated, v_block, v_mask)

def set_word(words, block, mask):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if block == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, set_word(words.tail, block - 1, mask))

def count_marked(words, remaining):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if remaining >= 24:
        return popcount(words.head, 24) + count_marked(words.tail, remaining - 24)
      else:
        return popcount(words.head, remaining)

def popcount(word, bits):
  if bits == 0:
    return 0
  else:
    return (word & 1) + popcount(word >> 1, bits - 1)
