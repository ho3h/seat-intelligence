def prog(xs):
  return sort_dedup(xs)

def sort_dedup(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      sorted_tail = sort_dedup(xs.tail)
      return insert_unique(xs.head, sorted_tail)

def insert_unique(x, xs):
  match xs:
    case List/Nil:
      return List/Cons(x, List/Nil)
    case List/Cons:
      if x < xs.head:
        return List/Cons(x, xs)
      else:
        if x == xs.head:
          return xs
        else:
          rest = insert_unique(x, xs.tail)
          return List/Cons(xs.head, rest)
