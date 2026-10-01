def prog(x):
  (n, edges) = x
  colors_rev = color_vertices(0, n, edges, [])
  return reverse_list(colors_rev, [])

def color_vertices(v, n, edges, colors_rev):
  if v == n:
    return colors_rev
  else:
    used = collect_used(v, edges, colors_rev, [])
    color = find_available(used, 0)
    return color_vertices(v + 1, n, edges, List/Cons(color, colors_rev))

def collect_used(v, edges, colors_rev, used):
  match edges:
    case List/Nil:
      return used
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        if b < v:
          color = get_reverse(colors_rev, v - 1 - b)
          return collect_used(v, edges.tail, colors_rev, List/Cons(color, used))
        else:
          return collect_used(v, edges.tail, colors_rev, used)
      else:
        if b == v:
          if a < v:
            color = get_reverse(colors_rev, v - 1 - a)
            return collect_used(v, edges.tail, colors_rev, List/Cons(color, used))
          else:
            return collect_used(v, edges.tail, colors_rev, used)
        else:
          return collect_used(v, edges.tail, colors_rev, used)

def find_available(used, color):
  if contains_color(used, color):
    return find_available(used, color + 1)
  else:
    return color

def contains_color(xs, color):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == color:
        return 1
      else:
        return contains_color(xs.tail, color)

def get_reverse(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return get_reverse(xs.tail, index - 1)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))
