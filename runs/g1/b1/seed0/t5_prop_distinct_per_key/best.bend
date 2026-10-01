def prog(xs):
  return process(xs, [], [], [], [])

def process(xs, seen0, seen1, seen2, seen3):
  match xs:
    case List/Nil:
      return [length(seen0), length(seen1), length(seen2), length(seen3)]
    case List/Cons:
      (node, key, value) = xs.head
      if key == 0:
        return process(xs.tail, add_unique(seen0, value), seen1, seen2, seen3)
      else:
        if key == 1:
          return process(xs.tail, seen0, add_unique(seen1, value), seen2, seen3)
        else:
          if key == 2:
            return process(xs.tail, seen0, seen1, add_unique(seen2, value), seen3)
          else:
            return process(xs.tail, seen0, seen1, seen2, add_unique(seen3, value))

def add_unique(xs, value):
  if contains(xs, value):
    return xs
  else:
    return List/Cons(value, xs)

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)
