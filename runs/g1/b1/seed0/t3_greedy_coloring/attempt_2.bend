def prog(x):
  (n, edges) = x
  colors_rev = color_vertices(0, n, edges, [])
  return reverse_list(colors_rev, [])

def color_vertices(v, n, edges, colors_rev):
  if v == n:
    return colors_rev
  else:
    color = find_color(v, 0, edges, colors_rev)
    return color_vertices(v + 1, n, edges, List/Cons(color, colors_rev))

def find_color(v, color, edges, colors_rev):
  if has_conflict(v, color, edges, colors_rev):
    return find_color(v, color + 1, edges, colors_rev)
  else:
    return color

def has_conflict(v, color, edges, colors_rev):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      (a, b) = edges.head
      if a == v:
        if b < v:
          neighbor_color = get_reverse(colors_rev, v - 1 - b)
          if neighbor_color == color:
            return 1
          else:
            return has_conflict(v, color, edges.tail, colors_rev)
        else:
          return has_conflict(v, color, edges.tail, colors_rev)
      else:
        if b == v:
          if a < v:
            neighbor_color = get_reverse(colors_rev, v - 1 - a)
            if neighbor_color == color:
              return 1
            else:
              return has_conflict(v, color, edges.tail, colors_rev)
          else:
            return has_conflict(v, color, edges.tail, colors_rev)
        else:
          return has_conflict(v, color, edges.tail, colors_rev)

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
