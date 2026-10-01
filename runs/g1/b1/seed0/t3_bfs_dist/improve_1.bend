def prog(x):
  (n, s, edges) = x
  word_count = (n + 23) / 24
  empty = make_zero_words(word_count)
  visited = put_bit(empty, s)
  distances = make_distances(n)
  distances2 = dist_put(distances, s, 0)
  return bfs(edges, visited, visited, distances2, word_count, 0)

def make_zero_words(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zero_words(n - 1))

def make_distances(n):
  if n == 0:
    return []
  else:
    return List/Cons(16777215, make_distances(n - 1))

def dist_put(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, dist_put(xs.tail, i - 1, value))

def get_word(words, i):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return words.head
      else:
        return get_word(words.tail, i - 1)

def set_word_bit(words, i, mask):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, set_word_bit(words.tail, i - 1, mask))

def put_bit(words, vertex):
  word_index = vertex / 24
  bit_index = vertex % 24
  mask = 1 << bit_index
  return set_word_bit(words, word_index, mask)

def has_bit(words, vertex):
  word_index = vertex / 24
  bit_index = vertex % 24
  mask = 1 << bit_index
  return (get_word(words, word_index) & mask) != 0

def or_words(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(a.head | b.head, or_words(a.tail, b.tail))

def and_not_words(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      mask = 16777215 - b.head
      return List/Cons(a.head & mask, and_not_words(a.tail, b.tail))

def words_are_zero(words):
  match words:
    case List/Nil:
      return true
    case List/Cons:
      if words.head != 0:
        return false
      else:
        return words_are_zero(words.tail)

def gather_edges(edges, frontier, candidates):
  match edges:
    case List/Nil:
      return candidates
    case List/Cons:
      (u, v) = edges.head
      if has_bit(frontier, u):
        candidates2 = put_bit(candidates, v)
      else:
        candidates2 = candidates
      return gather_edges(edges.tail, frontier, candidates2)

def assign_frontier(distances, frontier, vertex, value):
  match distances:
    case List/Nil:
      return []
    case List/Cons:
      if has_bit(frontier, vertex):
        value2 = value
      else:
        value2 = distances.head
      return List/Cons(value2, assign_frontier(distances.tail, frontier, vertex + 1, value))

def bfs(edges, visited, frontier, distances, word_count, depth):
  empty = make_zero_words(word_count)
  candidates = gather_edges(edges, frontier, empty)
  next_frontier = and_not_words(candidates, visited)
  if words_are_zero(next_frontier):
    return distances
  else:
    next_depth = depth + 1
    distances2 = assign_frontier(distances, next_frontier, 0, next_depth)
    visited2 = or_words(visited, next_frontier)
    return bfs(edges, visited2, next_frontier, distances2, word_count, next_depth)
