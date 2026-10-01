def prog(x):
  (k, xs) = x
  sorted = sort_list(xs)
  return get_k(k, sorted)

def sort_list(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return insert_sorted(xs.head, sort_list(xs.tail))

def insert_sorted(x, xs):
  match xs:
    case List/Nil:
      return List/Cons(x, List/Nil)
    case List/Cons:
      if x <= xs.head:
        return List/Cons(x, xs)
      else:
        return List/Cons(xs.head, insert_sorted(x, xs.tail))

def get_k(k, xs):
  if k == 0:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return xs.head
  else:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return get_k(k - 1, xs.tail)
