def prog(x):
  (c, attrs) = x
  mapped = map_attrs(attrs, c)
  return count_conflicts(mapped, 0)

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
      return List/Cons((cluster, key, node, value), rest)

def has_lower(attrs, cluster, key, node):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (other_cluster, other_key, other_node, other_value) = attrs.head
      if other_cluster == cluster:
        if other_key == key:
          if other_node < node:
            return 1
          else:
            return has_lower(attrs.tail, cluster, key, node)
        else:
          return has_lower(attrs.tail, cluster, key, node)
      else:
        return has_lower(attrs.tail, cluster, key, node)

def has_diff(attrs, cluster, key, value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (other_cluster, other_key, other_node, other_value) = attrs.head
      if other_cluster == cluster:
        if other_key == key:
          if other_value != value:
            return 1
          else:
            return has_diff(attrs.tail, cluster, key, value)
        else:
          return has_diff(attrs.tail, cluster, key, value)
      else:
        return has_diff(attrs.tail, cluster, key, value)

def count_conflicts(attrs, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (cluster, key, node, value) = attrs.head
      lower = has_lower(attrs, cluster, key, node)
      if lower == 0:
        different = has_diff(attrs, cluster, key, value)
        if different == 1:
          return count_conflicts(attrs.tail, acc + 1)
        else:
          return count_conflicts(attrs.tail, acc)
      else:
        return count_conflicts(attrs.tail, acc)
