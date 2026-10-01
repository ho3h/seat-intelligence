def prog(xs):
  return sort_desc(xs)

def sort_desc(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      sorted_tail = sort_desc(xs.tail)
      return insert_desc(xs.head, sorted_tail)

def insert_desc(value, xs):
  match xs:
    case List/Nil:
      return List/Cons(value, List/Nil)
    case List/Cons:
      if value >= xs.head:
        return List/Cons(value, xs)
      else:
        return List/Cons(xs.head, insert_desc(value, xs.tail))
