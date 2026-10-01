def prog(xs):
  return quick_count(xs)

def quick_count(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      size = list_length(xs)
      pivot = list_nth(xs, size / 2)
      (less, greater, cross) = partition(xs, pivot, [], [], 0, 0, 0)
      return quick_count(less) + quick_count(greater) + cross

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def list_nth(xs, n):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if n == 0:
        return xs.head
      else:
        return list_nth(xs.tail, n - 1)

def partition(xs, pivot, less, greater, greater_seen, equal_seen, cross):
  match xs:
    case List/Nil:
      return (less, greater, cross)
    case List/Cons:
      if xs.head < pivot:
        return partition(xs.tail, pivot, List/Cons(xs.head, less), greater, greater_seen, equal_seen, cross + greater_seen + equal_seen)
      else:
        if xs.head == pivot:
          return partition(xs.tail, pivot, less, greater, greater_seen, equal_seen + 1, cross + greater_seen)
        else:
          return partition(xs.tail, pivot, less, List/Cons(xs.head, greater), greater_seen + 1, equal_seen, cross)
