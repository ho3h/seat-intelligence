def prog(x):
  (xs, t) = x
  return search(xs, t, 0)

def search(xs, t, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if xs.head == t:
        return i
      else:
        if xs.head > t:
          return 16777215
        else:
          return search(xs.tail, t, i + 1)
