def prog(x):
  (c, attrs) = x
  mapped = map_attrs(attrs, c)
  return count_clusters(c, mapped, 0, 0)

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

def map_attrs(attrs, c):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      cluster = at(c, node)
      rest = map_attrs(attrs.tail, c)
      return List/Cons((cluster, key, value), rest)

def has_conflict(attrs, cluster, key, seen, first_value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (other_cluster, other_key, other_value) = attrs.head
      if other_cluster == cluster:
        if other_key == key:
          if seen == 0:
            return has_conflict(attrs.tail, cluster, key, 1, other_value)
          else:
            if other_value != first_value:
              return 1
            else:
              return has_conflict(attrs.tail, cluster, key, seen, first_value)
        else:
          return has_conflict(attrs.tail, cluster, key, seen, first_value)
      else:
        return has_conflict(attrs.tail, cluster, key, seen, first_value)

def count_keys(attrs, cluster, key):
  if key == 4:
    return 0
  else:
    conflict = has_conflict(attrs, cluster, key, 0, 0)
    rest = count_keys(attrs, cluster, key + 1)
    return conflict + rest

def count_clusters(c, attrs, index, acc):
  match c:
    case List/Nil:
      return acc
    case List/Cons:
      if c.head == index:
        conflicts = count_keys(attrs, index, 0)
        return count_clusters(c.tail, attrs, index + 1, acc + conflicts)
      else:
        return count_clusters(c.tail, attrs, index + 1, acc)
