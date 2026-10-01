def prog(x):
  (xs, ys) = x
  return merge_dc(xs, ys)

def merge_dc(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          n = length(xs)
          if n <= 1:
            return merge_seq(xs, ys)
          else:
            (left, right) = split_at(xs, n / 2)
            pivot = last(left)
            (ys_left, ys_right) = split_by(ys, pivot)
            merged_left = merge_dc(left, ys_left)
            merged_right = merge_dc(right, ys_right)
            return append(merged_left, merged_right)

def merge_seq(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head <= ys.head:
            return List/Cons(xs.head, merge_seq(xs.tail, ys))
          else:
            return List/Cons(ys.head, merge_seq(xs, ys.tail))

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def split_at(xs, n):
  switch n:
    case 0:
      return ([], xs)
    case _:
      match xs:
        case List/Nil:
          return ([], [])
        case List/Cons:
          (left, right) = split_at(xs.tail, n - 1)
          return (List/Cons(xs.head, left), right)

def last(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs.head
        case List/Cons:
          return last(xs.tail)

def split_by(ys, pivot):
  match ys:
    case List/Nil:
      return ([], [])
    case List/Cons:
      if ys.head <= pivot:
        (left, right) = split_by(ys.tail, pivot)
        return (List/Cons(ys.head, left), right)
      else:
        return ([], ys)

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))
