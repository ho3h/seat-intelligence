def prog(x):
  (n, edges) = x
  colors = make_colors((n + 11) / 12)
  return count_components(0, n, edges, colors, 0)

def make_colors(count):
  switch count:
    case 0:
      return []
    case _:
      return List/Cons(0, make_colors(count - 1))

def get_chunk(chunks, index):
  match chunks:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return chunks.head
      else:
        return get_chunk(chunks.tail, index - 1)

def get_color(chunks, vertex):
  chunk_index = vertex / 12
  shift = (vertex % 12) * 2
  chunk = get_chunk(chunks, chunk_index)
  return (chunk >> shift) & 3

def read_or_set_color(chunks, chunk_index, shift, expected):
  match chunks:
    case List/Nil:
      return (0, [])
    case List/Cons:
      if chunk_index == 0:
        color = (chunks.head >> shift) & 3
        if color == 0:
          mask = 3 << shift
          cleared = chunks.head & (16777215 ^ mask)
          new_chunk = cleared | (expected << shift)
          return (0, List/Cons(new_chunk, chunks.tail))
        else:
          return (color, chunks)
      else:
        (color, new_tail) = read_or_set_color(chunks.tail, chunk_index - 1, shift, expected)
        if color == 0:
          return (color, List/Cons(chunks.head, new_tail))
        else:
          return (color, chunks)

def other_color(color):
  if color == 1:
    return 2
  else:
    return 1

def add_neighbor(vertex, expected, stack, colors, bad):
  chunk_index = vertex / 12
  shift = (vertex % 12) * 2
  (color, new_colors) = read_or_set_color(colors, chunk_index, shift, expected)
  if color == 0:
    new_stack = List/Cons(vertex, stack)
    return (new_stack, new_colors, bad)
  else:
    if color == expected:
      return (stack, colors, bad)
    else:
      return (stack, colors, 1)

def scan_edges(edges, vertex, expected, stack, colors, bad):
  match edges:
    case List/Nil:
      return (stack, colors, bad)
    case List/Cons:
      (a, b) = edges.head
      if a == vertex:
        (stack2, colors2, bad2) = add_neighbor(b, expected, stack, colors, bad)
        return scan_edges(edges.tail, vertex, expected, stack2, colors2, bad2)
      else:
        if b == vertex:
          (stack2, colors2, bad2) = add_neighbor(a, expected, stack, colors, bad)
          return scan_edges(edges.tail, vertex, expected, stack2, colors2, bad2)
        else:
          return scan_edges(edges.tail, vertex, expected, stack, colors, bad)

def explore(stack, edges, colors, bad):
  match stack:
    case List/Nil:
      return (colors, bad)
    case List/Cons:
      vertex = stack.head
      rest = stack.tail
      color = get_color(colors, vertex)
      expected = other_color(color)
      (stack2, colors2, bad2) = scan_edges(edges, vertex, expected, rest, colors, bad)
      return explore(stack2, edges, colors2, bad2)

def count_components(i, n, edges, colors, count):
  if i == n:
    return count
  else:
    color = get_color(colors, i)
    if color != 0:
      return count_components(i + 1, n, edges, colors, count)
    else:
      chunk_index = i / 12
      shift = (i % 12) * 2
      (old_color, colors2) = read_or_set_color(colors, chunk_index, shift, 1)
      (colors3, bad) = explore(List/Cons(i, []), edges, colors2, 0)
      if bad == 0:
        return count_components(i + 1, n, edges, colors3, count + 1)
      else:
        return count_components(i + 1, n, edges, colors3, count)
