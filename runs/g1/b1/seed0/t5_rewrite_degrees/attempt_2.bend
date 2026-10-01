def prog(x):
  (clusters, edges) = x
  return build_degrees(clusters, clusters, 0, edges)

def build_degrees(all_clusters, remaining, index, edges):
  match remaining:
    case List/Nil:
      return []
    case List/Cons:
      rest = build_degrees(all_clusters, remaining.tail, index + 1, edges)
      if remaining.head == index:
        degree = count_neighbors(all_clusters, edges, index, [], 0)
        return List/Cons(degree, rest)
      else:
        return rest

def count_neighbors(clusters, edges, target, seen, count):
  match edges:
    case List/Nil:
      return count
    case List/Cons:
      (u, v) = edges.head
      a = lookup(clusters, u)
      b = lookup(clusters, v)
      if a == b:
        return count_neighbors(clusters, edges.tail, target, seen, count)
      else:
        if a == target:
          if contains(seen, b) == 1:
            return count_neighbors(clusters, edges.tail, target, seen, count)
          else:
            return count_neighbors(clusters, edges.tail, target, List/Cons(b, seen), count + 1)
        else:
          if b == target:
            if contains(seen, a) == 1:
              return count_neighbors(clusters, edges.tail, target, seen, count)
            else:
              return count_neighbors(clusters, edges.tail, target, List/Cons(a, seen), count + 1)
          else:
            return count_neighbors(clusters, edges.tail, target, seen, count)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def lookup(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return lookup(xs.tail, index - 1)
