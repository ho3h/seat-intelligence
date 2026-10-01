def prog(x):
  (n, s, edges) = x
  adjacency = make_adjacency(n)
  adjacency2 = build_adjacency(edges, adjacency)
  word_count = (n + 23) / 24
  visited = make_zero_words(word_count)
  visited2 = put_bit(visited, s)
  distances = make_distances(n)
  distances2 = dist_put(distances, s, 0)
  frontier = List/Cons(s, [])
  return bfs(adjacency2, frontier, visited2, distances2, 1)

def make_adjacency(n):
  if n == 0:
    return []
  else:
    return List/Cons([], make_adjacency(n - 1))

def build_adjacency(edges, adjacency):
  match edges:
    case List/Nil:
      return adjacency
    case List/Cons:
      (u, v) = edges.head
      adjacency2 = add_neighbor(adjacency, u, v)
      return build_adjacency(edges.tail, adjacency2)

def add_neighbor(adjacency, u, v):
  match adjacency:
    case List/Nil:
      return []
    case List/Cons:
      if u == 0:
        return List/Cons(List/Cons(v, adjacency.head), adjacency.tail)
      else:
        tail2 = add_neighbor(adjacency.tail, u - 1, v)
        return List/Cons(adjacency.head, tail2)

def list_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_at(xs.tail, i - 1)

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

def make_zero_words(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zero_words(n - 1))

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

def expand_neighbors(neighbors, visited, distances, next_frontier, next_depth):
  match neighbors:
    case List/Nil:
      return (visited, distances, next_frontier)
    case List/Cons:
      v = neighbors.head
      if has_bit(visited, v):
        return expand_neighbors(neighbors.tail, visited, distances, next_frontier, next_depth)
      else:
        visited2 = put_bit(visited, v)
        distances2 = dist_put(distances, v, next_depth)
        next2 = List/Cons(v, next_frontier)
        return expand_neighbors(neighbors.tail, visited2, distances2, next2, next_depth)

def expand_frontier(frontier, adjacency, visited, distances, next_frontier, next_depth):
  match frontier:
    case List/Nil:
      return (visited, distances, next_frontier)
    case List/Cons:
      neighbors = list_at(adjacency, frontier.head)
      (visited2, distances2, next2) = expand_neighbors(neighbors, visited, distances, next_frontier, next_depth)
      return expand_frontier(frontier.tail, adjacency, visited2, distances2, next2, next_depth)

def bfs(adjacency, frontier, visited, distances, depth):
  match frontier:
    case List/Nil:
      return distances
    case List/Cons:
      next_depth = depth + 1
      (visited2, distances2, next_frontier) = expand_frontier(frontier, adjacency, visited, distances, [], next_depth)
      return bfs(adjacency, next_frontier, visited2, distances2, next_depth)
