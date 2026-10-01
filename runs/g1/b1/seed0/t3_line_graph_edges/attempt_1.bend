def prog(x):
  (n, edges) = x
  return count_pairs(edges, 0)

def count_pairs(edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      count = count_with(edges.head, edges.tail, 0)
      return count_pairs(edges.tail, acc + count)

def count_with(edge, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edge
      (a, b) = edges.head
      if (u == a) | (u == b) | (v == a) | (v == b):
        return count_with(edge, edges.tail, acc + 1)
      else:
        return count_with(edge, edges.tail, acc)
