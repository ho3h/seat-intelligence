def prog(x):
  (n, edges) = x
  adj0 = empty_adjacency(n)
  adj = build_adjacency(edges, adj0)
  vertices = make_vertices(0, n)
  candidates = attach_rows(vertices, adj)
  if n == 0:
    return expand(candidates, 0, 0)
  else:
    return expand(candidates, 0, 1)

def empty_words(n):
  if n == 0:
    return []
  else:
    if n > 24:
      return List/Cons(0, empty_words(n - 24))
    else:
      return List/Cons(0, [])

def empty_adjacency(n):
  if n == 0:
    return []
  else:
    return List/Cons(empty_words(n), empty_adjacency(n - 1))

def make_vertices(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_vertices(i + 1, n))

def build_adjacency(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = set_edge_at(adj, u, v)
      adj2 = set_edge_at(adj1, v, u)
      return build_adjacency(edges.tail, adj2)

def set_edge_at(rows, row_idx, col_idx):
  match rows:
    case List/Nil:
      return []
    case List/Cons:
      if row_idx == 0:
        return List/Cons(set_bit(rows.head, col_idx), rows.tail)
      else:
        return List/Cons(rows.head, set_edge_at(rows.tail, row_idx - 1, col_idx))

def set_bit(words, idx):
  word_idx = idx / 24
  bit_idx = idx % 24
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if word_idx == 0:
        mask = 1 << bit_idx
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, set_bit(words.tail, idx - 24))

def get_at(xs, idx):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return xs.head
      else:
        return get_at(xs.tail, idx - 1)

def attach_rows(vertices, adj):
  match vertices:
    case List/Nil:
      return []
    case List/Cons:
      row = get_at(adj, vertices.head)
      return List/Cons((vertices.head, row), attach_rows(vertices.tail, adj))

def has_edge(a, b):
  (id_a, row_a) = a
  (id_b, row_b) = b
  word = get_at(row_a, id_b / 24)
  mask = 1 << (id_b % 24)
  return (word & mask) != 0

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def touches_any(v, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if has_edge(v, xs.head):
        return 1
      else:
        return touches_any(v, xs.tail)

def build_color_class(remaining, picked, rejected):
  match remaining:
    case List/Nil:
      return (picked, rejected)
    case List/Cons:
      if touches_any(remaining.head, picked) == 1:
        return build_color_class(
          remaining.tail,
          picked,
          List/Cons(remaining.head, rejected)
        )
      else:
        return build_color_class(
          remaining.tail,
          List/Cons(remaining.head, picked),
          rejected
        )

def add_color(picked, color, acc):
  match picked:
    case List/Nil:
      return acc
    case List/Cons:
      return List/Cons((picked.head, color), add_color(picked.tail, color, acc))

def color_loop(remaining, color, acc):
  match remaining:
    case List/Nil:
      return acc
    case List/Cons:
      (picked, rejected) = build_color_class(remaining, [], [])
      acc2 = add_color(picked, color, acc)
      return color_loop(rejected, color + 1, acc2)

def colorize(candidates):
  return color_loop(candidates, 1, [])

def ordered_neighbors(order, v):
  match order:
    case List/Nil:
      return []
    case List/Cons:
      (u, color) = order.head
      rest = ordered_neighbors(order.tail, v)
      if has_edge(v, u):
        return List/Cons(u, rest)
      else:
        return rest

def expand(candidates, size, best):
  if size > best:
    return expand_with_best(candidates, size, size)
  else:
    return expand_with_best(candidates, size, best)

def expand_with_best(candidates, size, best):
  if size + list_length(candidates) <= best:
    return best
  else:
    match candidates:
      case List/Nil:
        return best
      case List/Cons:
        order = colorize(candidates)
        return expand_order(order, size, best)

def expand_order(order, size, best):
  match order:
    case List/Nil:
      return best
    case List/Cons:
      (v, bound) = order.head
      if size + bound <= best:
        return best
      else:
        next_candidates = ordered_neighbors(order.tail, v)
        best1 = expand(next_candidates, size + 1, best)
        return expand_order(order.tail, size, best1)
