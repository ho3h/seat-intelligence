def prog(x):
  (n, edges) = x
  adj = build_adj(edges, n, 0)
  reverse_adj = build_adj(edges, n, 1)
  words = n / 24
  if n % 24 == 0:
    empty_bits = zero_bits(words)
  else:
    empty_bits = zero_bits(words + 1)
  (seen, finish) = first_pass(adj, n, 0, empty_bits, List/Nil)
  (assigned, pairs) = second_pass(finish, reverse_adj, empty_bits, List/Nil)
  return make_output(pairs, n, 0)

def zero_bits(words):
  if words == 0:
    return List/Nil
  else:
    return List/Cons(0, zero_bits(words - 1))

def build_adj(edges, n, reverse):
  if n == 0:
    return List/Nil
  else:
    return build_adj_range(edges, 0, n, reverse)

def build_adj_range(edges, lo, hi, reverse):
  if hi - lo == 1:
    row = collect_outgoing(edges, lo, reverse)
    return List/Cons(row, List/Nil)
  else:
    mid = (lo + hi) / 2
    (left_edges, right_edges) = split_edges(edges, mid, reverse)
    left_rows = build_adj_range(left_edges, lo, mid, reverse)
    right_rows = build_adj_range(right_edges, mid, hi, reverse)
    return concat(left_rows, right_rows)

def split_edges(edges, mid, reverse):
  match edges:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (u, v) = edges.head
      (left, right) = split_edges(edges.tail, mid, reverse)
      if reverse == 0:
        if u < mid:
          return (List/Cons(edges.head, left), right)
        else:
          return (left, List/Cons(edges.head, right))
      else:
        if v < mid:
          return (List/Cons(edges.head, left), right)
        else:
          return (left, List/Cons(edges.head, right))

def concat(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, concat(xs.tail, ys))

def collect_outgoing(edges, source, reverse):
  match edges:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v) = edges.head
      rest = collect_outgoing(edges.tail, source, reverse)
      if reverse == 0:
        if u == source:
          return List/Cons(v, rest)
        else:
          return rest
      else:
        if v == source:
          return List/Cons(u, rest)
        else:
          return rest

def nth_row(rows, i):
  match rows:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return rows.head
      else:
        return nth_row(rows.tail, i - 1)

def nth_word(words, i):
  match words:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return words.head
      else:
        return nth_word(words.tail, i - 1)

def replace_word(words, i, mask):
  match words:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(words.head | mask, words.tail)
      else:
        return List/Cons(words.head, replace_word(words.tail, i - 1, mask))

def bit_seen(bits, vertex):
  word_index = vertex / 24
  bit_index = vertex % 24
  word = nth_word(bits, word_index)
  mask = 1 << bit_index
  if (word & mask) != 0:
    return 1
  else:
    return 0

def set_bit(bits, vertex):
  word_index = vertex / 24
  bit_index = vertex % 24
  mask = 1 << bit_index
  return replace_word(bits, word_index, mask)

def first_frame(adj, stack, seen, finish):
  match stack:
    case List/Nil:
      return (seen, finish)
    case List/Cons:
      (vertex, neighbors) = stack.head
      rest = stack.tail
      match neighbors:
        case List/Nil:
          next_finish = List/Cons(vertex, finish)
          return first_frame(adj, rest, seen, next_finish)
        case List/Cons:
          neighbor = neighbors.head
          remaining = neighbors.tail
          if bit_seen(seen, neighbor) == 1:
            next_stack = List/Cons((vertex, remaining), rest)
            return first_frame(adj, next_stack, seen, finish)
          else:
            next_seen = set_bit(seen, neighbor)
            child_neighbors = nth_row(adj, neighbor)
            child_frame = (neighbor, child_neighbors)
            parent_frame = (vertex, remaining)
            next_stack = List/Cons(child_frame, List/Cons(parent_frame, rest))
            return first_frame(adj, next_stack, next_seen, finish)

def first_pass(adj, n, source, seen, finish):
  if source == n:
    return (seen, finish)
  else:
    if bit_seen(seen, source) == 1:
      return first_pass(adj, n, source + 1, seen, finish)
    else:
      next_seen = set_bit(seen, source)
      neighbors = nth_row(adj, source)
      start = List/Cons((source, neighbors), List/Nil)
      (after_seen, after_finish) = first_frame(adj, start, next_seen, finish)
      return first_pass(adj, n, source + 1, after_seen, after_finish)

def discover_neighbors(neighbors, stack, assigned, component):
  match neighbors:
    case List/Nil:
      return (stack, assigned, component)
    case List/Cons:
      vertex = neighbors.head
      rest = neighbors.tail
      if bit_seen(assigned, vertex) == 1:
        return discover_neighbors(rest, stack, assigned, component)
      else:
        next_assigned = set_bit(assigned, vertex)
        next_stack = List/Cons(vertex, stack)
        next_component = List/Cons(vertex, component)
        return discover_neighbors(rest, next_stack, next_assigned, next_component)

def collect_component(adj, stack, assigned, component):
  match stack:
    case List/Nil:
      return (assigned, component)
    case List/Cons:
      vertex = stack.head
      rest = stack.tail
      neighbors = nth_row(adj, vertex)
      (next_stack, next_assigned, next_component) =
        discover_neighbors(neighbors, rest, assigned, component)
      return collect_component(adj, next_stack, next_assigned, next_component)

def minimum(xs, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head < best:
        return minimum(xs.tail, xs.head)
      else:
        return minimum(xs.tail, best)

def add_labels(vertices, label, pairs):
  match vertices:
    case List/Nil:
      return pairs
    case List/Cons:
      return add_labels(vertices.tail, label, List/Cons((vertices.head, label), pairs))

def second_pass(order, reverse_adj, assigned, pairs):
  match order:
    case List/Nil:
      return (assigned, pairs)
    case List/Cons:
      vertex = order.head
      rest = order.tail
      if bit_seen(assigned, vertex) == 1:
        return second_pass(rest, reverse_adj, assigned, pairs)
      else:
        next_assigned = set_bit(assigned, vertex)
        component = List/Cons(vertex, List/Nil)
        (component_assigned, found_component) =
          collect_component(
            reverse_adj,
            List/Cons(vertex, List/Nil),
            next_assigned,
            component
          )
        label = minimum(found_component, vertex)
        next_pairs = add_labels(found_component, label, pairs)
        return second_pass(rest, reverse_adj, component_assigned, next_pairs)

def find_label(pairs, vertex):
  match pairs:
    case List/Nil:
      return vertex
    case List/Cons:
      (member, label) = pairs.head
      if member == vertex:
        return label
      else:
        return find_label(pairs.tail, vertex)

def make_output(pairs, n, vertex):
  if vertex == n:
    return List/Nil
  else:
    label = find_label(pairs, vertex)
    rest = make_output(pairs, n, vertex + 1)
    return List/Cons(label, rest)
