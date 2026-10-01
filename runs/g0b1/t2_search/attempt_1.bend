def prog(x):
  (xs, t) = x
  return find(xs, t, 0)

def find(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      h = xs.head
      if h == t:
        return i
      else:
        if h > t:
          return 16777215
        else:
          return find(xs.tail, t, i + 1)
