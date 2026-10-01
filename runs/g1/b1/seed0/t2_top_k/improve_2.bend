def prog(x):
  (k, xs) = x
  return quick_top(xs, k)

def quick_top(xs, k):
  if k == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        pivot = middle(xs, xs)
        (greater, equal, lesser, ng, ne) = partition(xs, pivot)
        if k <= ng:
          return quick_top(greater, k)
        else:
          sorted_greater = quick_top(greater, ng)
          remaining = k - ng
          if remaining <= ne:
            return append(sorted_greater, take_n(equal, remaining))
          else:
            sorted_lesser = quick_top(lesser, remaining - ne)
            return append(append(sorted_greater, equal), sorted_lesser)

def middle(slow, fast):
  match fast:
    case List/Nil:
      match slow:
        case List/Nil:
          return 0
        case List/Cons:
          return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          match slow:
            case List/Nil:
              return 0
            case List/Cons:
              return middle(slow.tail, fast.tail.tail)

def partition(xs, pivot):
  match xs:
    case List/Nil:
      return ([], [], [], 0, 0)
    case List/Cons:
      (greater, equal, lesser, ng, ne) = partition(xs.tail, pivot)
      if xs.head > pivot:
        return (List/Cons(xs.head, greater), equal, lesser, ng + 1, ne)
      else:
        if xs.head == pivot:
          return (greater, List/Cons(xs.head, equal), lesser, ng, ne + 1)
        else:
          return (greater, equal, List/Cons(xs.head, lesser), ng, ne)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def take_n(xs, n):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take_n(xs.tail, n - 1))
