def prog(x):
  (n, s, edges) = x
  return bfs([s], [], [s], [], edges)

def bfs(front, rear, seen, out_rev, edges):
  match front:
    case List/Nil:
      match rear:
        case List/Nil:
          return reverse(out_rev, [])
        case List/Cons:
          return bfs(reverse(rear, []), [], seen, out_rev, edges)
    case List/Cons:
      u = front.head
      neighbors = collect_neighbors(u, edges, [])
      ordered = merge_sort(neighbors)
      (next_rear, next_seen) = enqueue_neighbors(ordered, rear, seen)
      return bfs(front.tail, next_rear, next_seen, List/Cons(u, out_rev), edges)

def collect_neighbors(u, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = edges.head
      if a == u:
        return collect_neighbors(u, edges.tail, List/Cons(b, acc))
      else:
        if b == u:
          return collect_neighbors(u, edges.tail, List/Cons(a, acc))
        else:
          return collect_neighbors(u, edges.tail, acc)

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (left, right) = split_alternating(xs, [], [], 0)
      match right:
        case List/Nil:
          return xs
        case List/Cons:
          return merge(merge_sort(left), merge_sort(right))

def split_alternating(xs, left, right, turn):
  match xs:
    case List/Nil:
      return (left, right)
    case List/Cons:
      if turn == 0:
        return split_alternating(xs.tail, List/Cons(xs.head, left), right, 1)
      else:
        return split_alternating(xs.tail, left, List/Cons(xs.head, right), 0)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head < ys.head:
            return List/Cons(xs.head, merge(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge(xs, ys.tail))

def enqueue_neighbors(neighbors, rear, seen):
  match neighbors:
    case List/Nil:
      return (rear, seen)
    case List/Cons:
      if contains(seen, neighbors.head) == 0:
        next_rear = List/Cons(neighbors.head, rear)
        next_seen = List/Cons(neighbors.head, seen)
        return enqueue_neighbors(neighbors.tail, next_rear, next_seen)
      else:
        return enqueue_neighbors(neighbors.tail, rear, seen)

def contains(xs, v):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == v:
        return 1
      else:
        return contains(xs.tail, v)

def reverse(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse(xs.tail, List/Cons(xs.head, acc))
