def prog(xs):
  normalized = normalize(xs)
  sorted = sort(normalized)
  return collapse(sorted)

def normalize(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v, score) = xs.head
      tail = normalize(xs.tail)
      if u < v:
        return List/Cons((u, v, score), tail)
      else:
        return List/Cons((v, u, score), tail)

def split(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, List/Nil), List/Nil)
        case List/Cons:
          (left, right) = split(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split(xs)
          sorted_left = sort(left)
          sorted_right = sort(right)
          return merge(sorted_left, sorted_right)

def merge(left, right):
  match left:
    case List/Nil:
      return right
    case List/Cons:
      match right:
        case List/Nil:
          return left
        case List/Cons:
          (u1, v1, s1) = left.head
          (u2, v2, s2) = right.head
          if u1 < u2:
            tail = merge(left.tail, right)
            return List/Cons(left.head, tail)
          else:
            if u1 == u2:
              if v1 <= v2:
                tail = merge(left.tail, right)
                return List/Cons(left.head, tail)
              else:
                tail = merge(left, right.tail)
                return List/Cons(right.head, tail)
            else:
              tail = merge(left, right.tail)
              return List/Cons(right.head, tail)

def collapse(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v, score) = xs.head
      return collapse_group(xs.tail, u, v, score)

def collapse_group(xs, u, v, best):
  match xs:
    case List/Nil:
      return List/Cons((u, v, best), List/Nil)
    case List/Cons:
      (a, b, score) = xs.head
      if a == u:
        if b == v:
          if score > best:
            return collapse_group(xs.tail, u, v, score)
          else:
            return collapse_group(xs.tail, u, v, best)
        else:
          rest = collapse(xs)
          return List/Cons((u, v, best), rest)
      else:
        rest = collapse(xs)
        return List/Cons((u, v, best), rest)
