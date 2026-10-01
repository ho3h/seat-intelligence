def prog(x):
  (n, edges) = x
  base = count_components(n, edges, n)
  return find_cuts(0, n, edges, base)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def explore(v, removed, all_edges, seen):
  if v == removed:
    return seen
  else:
    if contains(seen, v) == 1:
      return seen
    else:
      seen2 = List/Cons(v, seen)
      return scan_edges(v, all_edges, all_edges, removed, seen2)

def scan_edges(v, all_edges, remaining, removed, seen):
  match remaining:
    case List/Nil:
      return seen
    case List/Cons:
      (a, b) = remaining.head
      if a == v:
        seen2 = explore(b, removed, all_edges, seen)
      else:
        if b == v:
          seen2 = explore(a, removed, all_edges, seen)
        else:
          seen2 = seen
      return scan_edges(v, all_edges, remaining.tail, removed, seen2)

def count_components(n, edges, removed):
  return count_scan(0, n, edges, removed, [], 0)

def count_scan(i, n, edges, removed, seen, count):
  if i == n:
    return count
  else:
    if i == removed:
      return count_scan(i + 1, n, edges, removed, seen, count)
    else:
      if contains(seen, i) == 1:
        return count_scan(i + 1, n, edges, removed, seen, count)
      else:
        seen2 = explore(i, removed, edges, seen)
        return count_scan(i + 1, n, edges, removed, seen2, count + 1)

def find_cuts(i, n, edges, base):
  if i == n:
    return []
  else:
    rest = find_cuts(i + 1, n, edges, base)
    after = count_components(n, edges, i)
    if after > base:
      return List/Cons(i, rest)
    else:
      return rest
