def prog(x):
  (n, s, edges) = x
  return reach(edges, [s], [s])

def reach(edges, visited, frontier):
  next_frontier = discover(edges, frontier, visited, [])
  match next_frontier:
    case List/Nil:
      return length(visited)
    case List/Cons:
      visited2 = add_all(next_frontier, visited)
      return reach(edges, visited2, next_frontier)

def discover(edges, frontier, visited, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if member(frontier, u) == 1:
        if member(visited, v) == 0:
          if member(acc, v) == 0:
            return discover(edges.tail, frontier, visited, List/Cons(v, acc))
          else:
            return discover(edges.tail, frontier, visited, acc)
        else:
          return discover(edges.tail, frontier, visited, acc)
      else:
        return discover(edges.tail, frontier, visited, acc)

def member(xs, target):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return member(xs.tail, target)

def add_all(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return add_all(xs.tail, List/Cons(xs.head, acc))

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)
