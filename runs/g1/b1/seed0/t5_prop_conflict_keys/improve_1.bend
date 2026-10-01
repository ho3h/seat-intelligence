def prog(x):
  (c, attrs) = x
  mapped = map_attrs(attrs, c)
  return collect_conflicts(mapped, [])

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

def has_later_conflict(attrs, cid, key, value):
  match attrs:
    case List/Nil:
      return 0
    case List/Cons:
      (other_cid, other_key, other_value) = attrs.head
      if other_cid == cid:
        if other_key == key:
          if other_value != value:
            return 1
          else:
            return has_later_conflict(attrs.tail, cid, key, value)
        else:
          return has_later_conflict(attrs.tail, cid, key, value)
      else:
        return has_later_conflict(attrs.tail, cid, key, value)

def insert_sorted_unique(xs, cid, key):
  match xs:
    case List/Nil:
      return [(cid, key)]
    case List/Cons:
      (head_cid, head_key) = xs.head
      if cid < head_cid:
        return List/Cons((cid, key), xs)
      else:
        if cid == head_cid:
          if key < head_key:
            return List/Cons((cid, key), xs)
          else:
            if key == head_key:
              return xs
            else:
              rest = insert_sorted_unique(xs.tail, cid, key)
              return List/Cons(xs.head, rest)
        else:
          rest = insert_sorted_unique(xs.tail, cid, key)
          return List/Cons(xs.head, rest)

def collect_conflicts(attrs, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (cid, key, value) = attrs.head
      if has_later_conflict(attrs.tail, cid, key, value) == 1:
        next_acc = insert_sorted_unique(acc, cid, key)
        return collect_conflicts(attrs.tail, next_acc)
      else:
        return collect_conflicts(attrs.tail, acc)
