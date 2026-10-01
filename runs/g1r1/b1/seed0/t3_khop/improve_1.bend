def prog(x):
  (n, s, k, edges) = x
  empty = make_words(n)
  seen = set_bit(empty, s)
  return bfs(edges, set_bit(empty, s), seen, 1, k)

def make_words(n):
  if n <= 24:
    return List/Cons(0, List/Nil)
  else:
    return List/Cons(0, make_words(n - 24))

def get_word(words, index):
  if index == 0:
    match words:
      case List/Nil:
        return 0
      case List/Cons:
        return words.head
  else:
    match words:
      case List/Nil:
        return 0
      case List/Cons:
        return get_word(words.tail, index - 1)

def replace_word(words, index, value):
  match words:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if index == 0:
        return List/Cons(value, words.tail)
      else:
        return List/Cons(words.head, replace_word(words.tail, index - 1, value))

def has_bit(words, vertex):
  index = vertex / 24
  offset = vertex % 24
  word = get_word(words, index)
  if ((word >> offset) & 1) == 1:
    return 1
  else:
    return 0

def set_bit(words, vertex):
  index = vertex / 24
  offset = vertex % 24
  word = get_word(words, index)
  return replace_word(words, index, word | (1 << offset))

def discover(candidate, frontier, seen, next, count, added):
  if has_bit(seen, candidate) == 1:
    return (next, seen, count, added)
  else:
    return (
      set_bit(next, candidate),
      set_bit(seen, candidate),
      count + 1,
      added + 1
    )

def scan_edges(edges, frontier, seen, next, count, added):
  match edges:
    case List/Nil:
      return (next, seen, count, added)
    case List/Cons:
      (u, v) = edges.head
      if has_bit(frontier, u) == 1:
        (next2, seen2, count2, added2) = discover(v, frontier, seen, next, count, added)
        return scan_edges(edges.tail, frontier, seen2, next2, count2, added2)
      else:
        if has_bit(frontier, v) == 1:
          (next2, seen2, count2, added2) = discover(u, frontier, seen, next, count, added)
          return scan_edges(edges.tail, frontier, seen2, next2, count2, added2)
        else:
          return scan_edges(edges.tail, frontier, seen, next, count, added)

def bfs(edges, frontier, seen, count, steps):
  if steps == 0:
    return count
  else:
    (next, seen2, count2, added) = scan_edges(edges, frontier, seen, List/Nil, count, 0)
    if added == 0:
      return count2
    else:
      return bfs(edges, next, seen2, count2, steps - 1)
