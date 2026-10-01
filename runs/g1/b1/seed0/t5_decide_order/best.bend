def prog(x):
  (tau, cands) = x
  accepted = filter(cands, tau)
  return sort(accepted)

def filter(xs, tau):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      rest = filter(xs.tail, tau)
      (u, v, score) = xs.head
      if score >= tau:
        return List/Cons(xs.head, rest)
      else:
        return rest

def split(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (left, right) = split(xs.tail)
      return (List/Cons(xs.head, right), left)

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
          if before(left.head, right.head):
            return List/Cons(left.head, merge(left.tail, right))
          else:
            return List/Cons(right.head, merge(left, right.tail))

def before(a, b):
  (au, av, ascore) = a
  (bu, bv, bscore) = b
  if ascore == bscore:
    if au == bu:
      return av <= bv
    else:
      return au < bu
  else:
    return ascore > bscore
