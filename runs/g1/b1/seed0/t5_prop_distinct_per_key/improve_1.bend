def prog(xs):
  return count_sorted(sort(project(xs)), 0, 0, 0, 0, 0, 0, 0)

def project(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      (node, key, value) = xs.head
      return List/Cons((key, value), project(xs.tail))

def sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          (left, right) = split(xs, 0)
          sorted_left = sort(left)
          sorted_right = sort(right)
          return merge(sorted_left, sorted_right)

def split(xs, flag):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split(xs.tail, 1 - flag)
      if flag == 0:
        return (List/Cons(xs.head, left), right)
      else:
        return (left, List/Cons(xs.head, right))

def before(a, b):
  (ka, va) = a
  (kb, vb) = b
  if ka < kb:
    return 1
  else:
    if ka == kb:
      if va <= vb:
        return 1
      else:
        return 0
    else:
      return 0

def merge(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if before(a.head, b.head) == 1:
            return List/Cons(a.head, merge(a.tail, b))
          else:
            return List/Cons(b.head, merge(a, b.tail))

def count_sorted(xs, has_prev, prev_key, prev_value, c0, c1, c2, c3):
  match xs:
    case List/Nil:
      return [c0, c1, c2, c3]
    case List/Cons:
      (key, value) = xs.head
      if has_prev == 0:
        return count_add(xs.tail, key, value, c0, c1, c2, c3)
      else:
        if key != prev_key:
          return count_add(xs.tail, key, value, c0, c1, c2, c3)
        else:
          if value != prev_value:
            return count_add(xs.tail, key, value, c0, c1, c2, c3)
          else:
            return count_sorted(xs.tail, 1, key, value, c0, c1, c2, c3)

def count_add(xs, key, value, c0, c1, c2, c3):
  if key == 0:
    return count_sorted(xs, 1, key, value, c0 + 1, c1, c2, c3)
  else:
    if key == 1:
      return count_sorted(xs, 1, key, value, c0, c1 + 1, c2, c3)
    else:
      if key == 2:
        return count_sorted(xs, 1, key, value, c0, c1, c2 + 1, c3)
      else:
        return count_sorted(xs, 1, key, value, c0, c1, c2, c3 + 1)
