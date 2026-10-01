def prog(x):
  (n, edges) = x
  adj = build_adjacency(0, n, edges)
  size = padded_size(n, 1)
  adj_tree = build_tree(adj, size)
  word_count = (n + 23) / 24
  return all_eccentricities(0, n, adj_tree, size, word_count)

def padded_size(n, size):
  if size >= n:
    return size
  else:
    return padded_size(n, size * 2)

def build_adjacency(i, n, edges):
  if i == n:
    return []
  else:
    neighbors = find_neighbors(i, edges, [])
    rest = build_adjacency(i + 1, n, edges)
    return List/Cons(neighbors, rest)

def find_neighbors(i, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      acc1 = maybe_prepend(u == i, v, acc)
      acc2 = maybe_prepend(v == i, u, acc1)
      return find_neighbors(i, edges.tail, acc2)

def maybe_prepend(condition, value, xs):
  if condition:
    return List/Cons(value, xs)
  else:
    return xs

def split_list(xs, count):
  if count == 0:
    return ([], xs)
  else:
    match xs:
      case List/Nil:
        return ([], [])
      case List/Cons:
        (left, rest) = split_list(xs.tail, count - 1)
        return (List/Cons(xs.head, left), rest)

def build_tree(xs, size):
  if size == 1:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return xs.head
  else:
    half = size / 2
    (left_items, right_items) = split_list(xs, half)
    left_tree = build_tree(left_items, half)
    right_tree = build_tree(right_items, half)
    return (left_tree, right_tree)

def tree_lookup(tree, index, size):
  if size == 1:
    return tree
  else:
    half = size / 2
    (left_tree, right_tree) = tree
    if index < half:
      return tree_lookup(left_tree, index, half)
    else:
      return tree_lookup(right_tree, index - half, half)

def zero_words(i, count):
  if i == count:
    return []
  else:
    return List/Cons(0, zero_words(i + 1, count))

def get_word(words, i):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return words.head
      else:
        return get_word(words.tail, i - 1)

def set_word(words, i, mask):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        rest = set_word(words.tail, i - 1, mask)
        return List/Cons(words.head, rest)

def has_vertex(words, vertex):
  chunk = vertex / 24
  bit = vertex % 24
  mask = 1 << bit
  word = get_word(words, chunk)
  if (word & mask) == 0:
    return 0
  else:
    return 1

def mark_vertex(words, vertex):
  chunk = vertex / 24
  bit = vertex % 24
  mask = 1 << bit
  return set_word(words, chunk, mask)

def expand_neighbors(neighbors, visited, next_frontier):
  match neighbors:
    case List/Nil:
      return (visited, next_frontier)
    case List/Cons:
      value = neighbors.head
      if has_vertex(visited, value) == 0:
        visited2 = mark_vertex(visited, value)
        next2 = List/Cons(value, next_frontier)
        return expand_neighbors(neighbors.tail, visited2, next2)
      else:
        return expand_neighbors(neighbors.tail, visited, next_frontier)

def expand_frontier(frontier, adj_tree, tree_size, visited, next_frontier):
  match frontier:
    case List/Nil:
      return (visited, next_frontier)
    case List/Cons:
      neighbors = tree_lookup(adj_tree, frontier.head, tree_size)
      (visited2, next2) = expand_neighbors(neighbors, visited, next_frontier)
      return expand_frontier(frontier.tail, adj_tree, tree_size, visited2, next2)

def bfs_eccentricity(adj_tree, tree_size, frontier, visited, level):
  (visited2, next_frontier) = expand_frontier(frontier, adj_tree, tree_size, visited, [])
  match next_frontier:
    case List/Nil:
      return level
    case List/Cons:
      return bfs_eccentricity(adj_tree, tree_size, next_frontier, visited2, level + 1)

def all_eccentricities(i, n, adj_tree, tree_size, word_count):
  if i == n:
    return []
  else:
    empty_words = zero_words(0, word_count)
    visited = mark_vertex(empty_words, i)
    start = List/Cons(i, [])
    eccentricity = bfs_eccentricity(adj_tree, tree_size, start, visited, 0)
    rest = all_eccentricities(i + 1, n, adj_tree, tree_size, word_count)
    return List/Cons(eccentricity, rest)
