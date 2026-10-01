def prog(x):
  (n, edges) = x
  colors = make_colors(n)
  (colors, bad) = process_roots(0, n, edges, colors, 0)
  if bad == 1:
    return make_fill(n, 16777215)
  else:
    return colors

def make_colors(n):
  if n == 0:
    return []
  else:
    return List/Cons(2, make_colors(n - 1))

def make_fill(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_fill(n - 1, value))

def list_get(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_get(xs.tail, i - 1)

def list_set(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, list_set(xs.tail, i - 1, value))

def list_append(xs, value):
  match xs:
    case List/Nil:
      return [value]
    case List/Cons:
      return List/Cons(xs.head, list_append(xs.tail, value))

def process_roots(i, n, edges, colors, bad):
  if bad == 1:
    return (colors, bad)
  else:
    if i == n:
      return (colors, bad)
    else:
      color = list_get(colors, i)
      if color == 2:
        colors = list_set(colors, i, 0)
        (colors, bad) = breadth_first(edges, colors, [i], 0)
        return process_roots(i + 1, n, edges, colors, bad)
      else:
        return process_roots(i + 1, n, edges, colors, bad)

def breadth_first(edges, colors, queue, bad):
  if bad == 1:
    return (colors, bad)
  else:
    match queue:
      case List/Nil:
        return (colors, bad)
      case List/Cons:
        current = queue.head
        current_color = list_get(colors, current)
        (colors, queue, bad) = scan_edges(current, current_color, edges, colors, queue.tail, bad)
        return breadth_first(edges, colors, queue, bad)

def scan_edges(current, current_color, edges, colors, queue, bad):
  if bad == 1:
    return (colors, queue, bad)
  else:
    match edges:
      case List/Nil:
        return (colors, queue, bad)
      case List/Cons:
        (u, v) = edges.head
        if u == current:
          (colors, queue, bad) = visit_neighbor(v, current_color, colors, queue, bad)
          return scan_edges(current, current_color, edges.tail, colors, queue, bad)
        else:
          if v == current:
            (colors, queue, bad) = visit_neighbor(u, current_color, colors, queue, bad)
            return scan_edges(current, current_color, edges.tail, colors, queue, bad)
          else:
            return scan_edges(current, current_color, edges.tail, colors, queue, bad)

def visit_neighbor(neighbor, current_color, colors, queue, bad):
  expected = 1 - current_color
  neighbor_color = list_get(colors, neighbor)
  if neighbor_color == 2:
    colors = list_set(colors, neighbor, expected)
    queue = list_append(queue, neighbor)
    return (colors, queue, bad)
  else:
    if neighbor_color != expected:
      return (colors, queue, 1)
    else:
      return (colors, queue, bad)
