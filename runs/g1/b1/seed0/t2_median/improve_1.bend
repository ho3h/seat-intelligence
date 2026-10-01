def prog(xs):
  k = length(xs) / 2
  return select(xs, k)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def head_or_zero(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return xs.head

def middle(slow, fast):
  match fast:
    case List/Nil:
      return head_or_zero(slow)
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return head_or_zero(slow)
        case List/Cons:
          return middle(slow.tail, fast.tail.tail)

def partition(xs, pivot, less, greater, less_count, equal_count):
  match xs:
    case List/Nil:
      return ((less, less_count), (equal_count, greater))
    case List/Cons:
      if xs.head < pivot:
        return partition(
          xs.tail,
          pivot,
          List/Cons(xs.head, less),
          greater,
          less_count + 1,
          equal_count
        )
      else:
        if xs.head == pivot:
          return partition(
            xs.tail,
            pivot,
            less,
            greater,
            less_count,
            equal_count + 1
          )
        else:
          return partition(
            xs.tail,
            pivot,
            less,
            List/Cons(xs.head, greater),
            less_count,
            equal_count
          )

def select(xs, k):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      pivot = middle(xs, xs)
      (left_info, right_info) = partition(xs, pivot, [], [], 0, 0)
      (less, less_count) = left_info
      (equal_count, greater) = right_info
      if k < less_count:
        return select(less, k)
      else:
        if k < less_count + equal_count:
          return pivot
        else:
          return select(greater, k - less_count - equal_count)
