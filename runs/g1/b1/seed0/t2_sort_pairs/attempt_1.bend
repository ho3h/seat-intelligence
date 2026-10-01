def prog(x):
  return sort_pairs(x)

def sort_pairs(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      sorted_tail = sort_pairs(xs.tail)
      return insert_pair(xs.head, sorted_tail)

def insert_pair(pair, xs):
  match xs:
    case List/Nil:
      return List/Cons(pair, List/Nil)
    case List/Cons:
      (key, value) = pair
      (head_key, head_value) = xs.head
      if key <= head_key:
        return List/Cons(pair, xs)
      else:
        inserted_tail = insert_pair(pair, xs.tail)
        return List/Cons(xs.head, inserted_tail)
