def list_len(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_len(xs.tail)

def take(n, xs):
  if n == 0:
    return []
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, take(n - 1, xs.tail))

def drop(n, xs):
  if n == 0:
    return xs
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return drop(n - 1, xs.tail)

def build_rec(n, xs):
  if n == 0:
    return Gtree/C0
  else:
    left_n = (n - 1) / 2
    right_n = n / 2
    left_part = take(left_n, xs)
    after_left = drop(left_n, xs)
    match after_left:
      case List/Nil:
        return Gtree/C0
      case List/Cons:
        root = after_left.head
        right_part = after_left.tail
        left_tree = build_rec(left_n, left_part)
        match left_tree:
          case _:
            right_tree = build_rec(right_n, right_part)
            match right_tree:
              case _:
                return Gtree/C1(left_tree, root, right_tree)

def force_tree(t):
  match t:
    case Gtree/C0:
      return Gtree/C0
    case Gtree/C1:
      left = force_tree(t.f0)
      match left:
        case _:
          right = force_tree(t.f2)
          match right:
            case _:
              return Gtree/C1(left, t.f1, right)

def prog(xs):
  n = list_len(xs)
  tree = build_rec(n, xs)
  forced = force_tree(tree)
  match forced:
    case _:
      return forced
