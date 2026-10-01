def prog(x):
  (n, edges) = x
  (vertices, odds) = collect(edges, [], [])
  match vertices:
    case List/Nil:
      return 16777215
    case List/Cons:
      reached = closure(List/Cons(vertices.head, List/Nil), edges)
      if length(reached) != length(vertices):
        return 16777215
      else:
        odd_count = length(odds)
        if odd_count == 0:
          return smallest(vertices)
        else:
          if odd_count == 2:
            return smallest(odds)
          else:
            return 16777215

def collect(edges, vertices, odds):
  match edges:
    case List/Nil:
      return (vertices, odds)
    case List/Cons:
      (u, v) = edges.head
      vertices1 = insert(vertices, u)
      vertices2 = insert(vertices1, v)
      odds1 = toggle(odds, u)
      odds2 = toggle(odds1, v)
      return collect(edges.tail, vertices2, odds2)

def contains(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains(xs.tail, x)

def insert(xs, x):
  if contains(xs, x) == 1:
    return xs
  else:
    return List/Cons(x, xs)

def remove_one(xs, x):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == x:
        return xs.tail
      else:
        return List/Cons(xs.head, remove_one(xs.tail, x))

def toggle(xs, x):
  if contains(xs, x) == 1:
    return remove_one(xs, x)
  else:
    return List/Cons(x, xs)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def smallest(xs):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      return smallest_from(xs.tail, xs.head)

def smallest_from(xs, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head < best:
        return smallest_from(xs.tail, xs.head)
      else:
        return smallest_from(xs.tail, best)

def sweep(edges, reached):
  match edges:
    case List/Nil:
      return reached
    case List/Cons:
      (u, v) = edges.head
      if contains(reached, u) == 1:
        reached1 = insert(reached, v)
        return sweep(edges.tail, reached1)
      else:
        if contains(reached, v) == 1:
          reached1 = insert(reached, u)
          return sweep(edges.tail, reached1)
        else:
          return sweep(edges.tail, reached)

def closure(reached, edges):
  expanded = sweep(edges, reached)
  if length(expanded) == length(reached):
    return expanded
  else:
    return closure(expanded, edges)
