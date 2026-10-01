def prog(x):
  (n, s, k, edges) = x
  prepared = prepare_edges(edges)
  empty = make_words(n)
  start = set_index(empty, s / 24, 1 << (s % 24))
  return bfs(prepared, n, start, start, 1, k)

def make_words(n):
  if n <= 24:
    return List/Cons(0, List/Nil)
  else:
    return List/Cons(0, make_words(n - 24))

def prepare_edges(edges):
  match edges:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v) = edges.head
      ui = u / 24
      um = 1 << (u % 24)
      vi = v / 24
      vm = 1 << (v % 24)
      return List/Cons(
        (u, ui, um, v, vi, vm),
        prepare_edges(edges.tail)
      )

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

def has_index(words, index, mask):
  word = get_word(words, index)
  if (word & mask) == 0:
    return 0
  else:
    return 1

def set_index(words, index, mask):
  word = get_word(words, index)
  return replace_word(words, index, word | mask)

def discover(candidate, index, mask, seen, next, count, added):
  if has_index(seen, index, mask) == 1:
    return (next, seen, count, added)
  else:
    return (
      set_index(next, index, mask),
      set_index(seen, index, mask),
      count + 1,
      added + 1
    )

def scan_edges(edges, frontier, seen, next, count, added):
  match edges:
    case List/Nil:
      return (next, seen, count, added)
    case List/Cons:
      (u, ui, um, v, vi, vm) = edges.head
      if has_index(frontier, ui, um) == 1:
        (next2, seen2, count2, added2) = discover(v, vi, vm, seen, next, count, added)
        return scan_edges(edges.tail, frontier, seen2, next2, count2, added2)
      else:
        if has_index(frontier, vi, vm) == 1:
          (next2, seen2, count2, added2) = discover(u, ui, um, seen, next, count, added)
          return scan_edges(edges.tail, frontier, seen2, next2, count2, added2)
        else:
          return scan_edges(edges.tail, frontier, seen, next, count, added)

def bfs(edges, n, frontier, seen, count, steps):
  if steps == 0:
    return count
  else:
    empty = make_words(n)
    (next, seen2, count2, added) = scan_edges(edges, frontier, seen, empty, count, 0)
    if added == 0:
      return count2
    else:
      return bfs(edges, n, next, seen2, count2, steps - 1)
