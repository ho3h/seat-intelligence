def prog(x):
  (n, edges) = x
  colors = make_colors(n)
  return count_components(0, n, edges, colors, 0)

def make_colors(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_colors(n - 1))

def get_color(colors, i):
  match colors:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return colors.head
      else:
        return get_color(colors.tail, i - 1)

def set_color(colors, i, value):
  match colors:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, colors.tail)
      else:
        tail = set_color(colors.tail, i - 1, value)
        return List/Cons(colors.head, tail)

def other_color(color):
  if color == 1:
    return 2
  else:
    return 1

def add_neighbor(vertex, expected, stack, colors, bad):
  color = get_color(colors, vertex)
  if color == 0:
    new_colors = set_color(colors, vertex, expected)
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
      colors2 = set_color(colors, i, 1)
      (colors3, bad) = explore(List/Cons(i, []), edges, colors2, 0)
      if bad == 0:
        return count_components(i + 1, n, edges, colors3, count + 1)
      else:
        return count_components(i + 1, n, edges, colors3, count)
