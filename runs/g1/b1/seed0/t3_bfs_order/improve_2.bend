def prog(x):
  (n, s, edges) = x
  arcs = make_arcs(edges, [])
  sorted_arcs = merge_sort(arcs)
  adj = build_adj(n, sorted_arcs, 0, [], [])
  return bfs([s], [], [s], [], adj)

def make_arcs(edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      next_acc = List/Cons((v, u), List/Cons((u, v), acc))
      return make_arcs(edges.tail, next_acc)

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

def pair_less(p, q):
  (a, b) = p
  (c, d) = q
  if a < c:
    return 1
  else:
    if a == c:
      if b < d:
        return 1
      else:
        return 0
    else:
      return 0

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if pair_less(xs.head, ys.head) == 1:
            return List/Cons(xs.head, merge(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge(xs, ys.tail))

def build_adj(n, arcs, u, cur_rev, out_rev):
  if u == n:
    return reverse(out_rev, [])
  else:
    match arcs:
      case List/Nil:
        next_out = List/Cons(reverse(cur_rev, []), out_rev)
        return build_adj(n, [], u + 1, [], next_out)
      case List/Cons:
        (a, b) = arcs.head
        if a == u:
          return build_adj(n, arcs.tail, u, List/Cons(b, cur_rev), out_rev)
        else:
          next_out = List/Cons(reverse(cur_rev, []), out_rev)
          return build_adj(n, arcs, u + 1, [], next_out)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def bfs(front, rear, seen, out_rev, adj):
  match front:
    case List/Nil:
      match rear:
        case List/Nil:
          return reverse(out_rev, [])
        case List/Cons:
          return bfs(reverse(rear, []), [], seen, out_rev, adj)
    case List/Cons:
      u = front.head
      neighbors = get_at(adj, u)
      (next_rear, next_seen) = enqueue_neighbors(neighbors, rear, seen)
      return bfs(front.tail, next_rear, next_seen, List/Cons(u, out_rev), adj)

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
