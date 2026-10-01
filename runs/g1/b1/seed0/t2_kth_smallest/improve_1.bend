def prog(x):
  (k, xs) = x
  return select_k(k, xs)

def select_k(k, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      pivot = middle_value(xs, xs)
      (less, less_count, equal_count, greater) = partition(xs, pivot)
      if k < less_count:
        return select_k(k, less)
      else:
        if k < less_count + equal_count:
          return pivot
        else:
          return select_k(k - less_count - equal_count, greater)

def middle_value(slow, fast):
  match fast:
    case List/Nil:
      return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          return middle_value(slow.tail, fast.tail.tail)

def partition(xs, pivot):
  match xs:
    case List/Nil:
      return (List/Nil, 0, 0, List/Nil)
    case List/Cons:
      (less, less_count, equal_count, greater) = partition(xs.tail, pivot)
      if xs.head < pivot:
        return (List/Cons(xs.head, less), less_count + 1, equal_count, greater)
      else:
        if xs.head == pivot:
          return (less, less_count, equal_count + 1, greater)
        else:
          return (less, less_count, equal_count, List/Cons(xs.head, greater))
