def prog(x):
  (c, mnl) = x
  bad_clusters = collect_bad(mnl, c)
  return scan_nodes(c, c, bad_clusters, 0)

def value_at(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return value_at(xs.tail, index - 1)

def collect_bad(pairs, c):
  match pairs:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = pairs.head
      ca = value_at(c, a)
      cb = value_at(c, b)
      rest = collect_bad(pairs.tail, c)
      if ca == cb:
        return List/Cons(ca, rest)
      else:
        return rest

def contains(xs, target):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(xs.tail, target)

def scan_nodes(all_nodes, xs, bad_clusters, index):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      rest = scan_nodes(all_nodes, xs.tail, bad_clusters, index + 1)
      if xs.head == index:
        flag = contains(bad_clusters, index)
        return List/Cons(flag, rest)
      else:
        return rest
