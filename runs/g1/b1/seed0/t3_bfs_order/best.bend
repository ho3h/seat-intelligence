def prog(x):
  (n, s, edges) = x
  return bfs([s], [s], [], edges)

def bfs(queue, seen, out_rev, edges):
  match queue:
    case List/Nil:
      return reverse(out_rev, [])
    case List/Cons:
      u = queue.head
      rest = queue.tail
      neighbors = collect_neighbors(u, edges, [])
      (next_queue, next_seen) = enqueue_neighbors(neighbors, rest, seen)
      return bfs(next_queue, next_seen, List/Cons(u, out_rev), edges)

def collect_neighbors(u, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = edges.head
      if a == u:
        updated = insert_sorted(b, acc)
        return collect_neighbors(u, edges.tail, updated)
      else:
        if b == u:
          updated = insert_sorted(a, acc)
          return collect_neighbors(u, edges.tail, updated)
        else:
          return collect_neighbors(u, edges.tail, acc)

def insert_sorted(v, xs):
  match xs:
    case List/Nil:
      return [v]
    case List/Cons:
      if v < xs.head:
        return List/Cons(v, xs)
      else:
        if v == xs.head:
          return xs
        else:
          tail = insert_sorted(v, xs.tail)
          return List/Cons(xs.head, tail)

def enqueue_neighbors(neighbors, queue, seen):
  match neighbors:
    case List/Nil:
      return (queue, seen)
    case List/Cons:
      if contains(seen, neighbors.head) == 0:
        next_queue = append_one(queue, neighbors.head)
        next_seen = List/Cons(neighbors.head, seen)
        return enqueue_neighbors(neighbors.tail, next_queue, next_seen)
      else:
        return enqueue_neighbors(neighbors.tail, queue, seen)

def contains(xs, v):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == v:
        return 1
      else:
        return contains(xs.tail, v)

def append_one(xs, v):
  match xs:
    case List/Nil:
      return [v]
    case List/Cons:
      tail = append_one(xs.tail, v)
      return List/Cons(xs.head, tail)

def reverse(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse(xs.tail, List/Cons(xs.head, acc))
