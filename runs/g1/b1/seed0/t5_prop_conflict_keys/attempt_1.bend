def prog(x):
  (c, attrs) = x
  mapped = map_attrs(attrs, c)
  rev = walk_clusters(c, mapped, 0, [])
  return reverse_list(rev, [])

def list_get(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_get(xs.tail, i - 1)

def map_attrs(attrs, c):
  match attrs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = attrs.head
      cid = list_get(c, node)
      rest = map_attrs(attrs.tail, c)
      return List/Cons((cid, key, value), rest)

def has_conflict(attrs, cid, key, seen, old_value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (attr_cid, attr_key, value) = attrs.head
      if attr_cid == cid:
        if attr_key == key:
          if seen == 0:
            return has_conflict(attrs.tail, cid, key, 1, value)
          else:
            if value != old_value:
              return 1
            else:
              return has_conflict(attrs.tail, cid, key, seen, old_value)
        else:
          return has_conflict(attrs.tail, cid, key, seen, old_value)
      else:
        return has_conflict(attrs.tail, cid, key, seen, old_value)

def add_conflicting_keys(attrs, cid, key, acc):
  if key == 4:
    return acc
  else:
    conflict = has_conflict(attrs, cid, key, 0, 0)
    if conflict == 1:
      next_acc = List/Cons((cid, key), acc)
      return add_conflicting_keys(attrs, cid, key + 1, next_acc)
    else:
      return add_conflicting_keys(attrs, cid, key + 1, acc)

def walk_clusters(c, attrs, i, acc):
  match c:
    case List/Nil:
      return acc
    case List/Cons:
      if c.head == i:
        next_acc = add_conflicting_keys(attrs, i, 0, acc)
        return walk_clusters(c.tail, attrs, i + 1, next_acc)
      else:
        return walk_clusters(c.tail, attrs, i + 1, acc)

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))
