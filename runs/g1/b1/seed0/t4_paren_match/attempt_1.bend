def prog(xs):
  return build(xs, [], 0)

def build(xs, rev, i):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == 40:
        j = find_forward(xs.tail, i + 1, 1)
      else:
        j = find_backward(rev, i - 1, 1)
      rest = build(xs.tail, List/Cons(xs.head, rev), i + 1)
      return List/Cons(j, rest)

def find_forward(xs, i, depth):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == 40:
        return find_forward(xs.tail, i + 1, depth + 1)
      else:
        if depth == 1:
          return i
        else:
          return find_forward(xs.tail, i + 1, depth - 1)

def find_backward(xs, i, depth):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == 40:
        if depth == 1:
          return i
        else:
          return find_backward(xs.tail, i - 1, depth - 1)
      else:
        return find_backward(xs.tail, i - 1, depth + 1)
