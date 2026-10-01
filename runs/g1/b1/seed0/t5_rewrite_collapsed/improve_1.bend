def prog(x):
  (clusters, edges) = x
  n = length(clusters)
  (keys, total) = collect(edges, clusters, n, [], 0)
  ordered = sort(keys)
  distinct = count_unique(ordered, 0, 0, 0)
  return total - distinct

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return at(xs.tail, i - 1)

def collect(edges, clusters, n, keys, total):
  match edges:
    case List/Nil:
      return (keys, total)
    case List/Cons:
      (u, v) = edges.head
      cu = at(clusters, u)
      cv = at(clusters, v)
      if cu == cv:
        return collect(edges.tail, clusters, n, keys, total + 1)
      else:
        if cu < cv:
          key = cu * n + cv
        else:
          key = cv * n + cu
        return collect(edges.tail, clusters, n, List/Cons(key, keys), total + 1)

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort(left)
          sorted_right = sort(right)
          return merge(sorted_left, sorted_right)

def merge(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if a.head < b.head:
            return List/Cons(a.head, merge(a.tail, b))
          else:
            return List/Cons(b.head, merge(a, b.tail))

def count_unique(xs, prev, started, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if started == 0:
        return count_unique(xs.tail, xs.head, 1, count + 1)
      else:
        if xs.head == prev:
          return count_unique(xs.tail, prev, started, count)
        else:
          return count_unique(xs.tail, xs.head, started, count + 1)
