def prog(x):
  (c, mnl) = x
  return collect(c, mnl, List/Nil)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def insert_sorted(pair, xs):
  match xs:
    case List/Nil:
      return List/Cons(pair, List/Nil)
    case List/Cons:
      (a, b) = pair
      (ha, hb) = xs.head
      if a < ha:
        return List/Cons(pair, xs)
      else:
        if a == ha:
          if b < hb:
            return List/Cons(pair, xs)
          else:
            return List/Cons(xs.head, insert_sorted(pair, xs.tail))
        else:
          return List/Cons(xs.head, insert_sorted(pair, xs.tail))

def collect(c, pairs, acc):
  match pairs:
    case List/Nil:
      return acc
    case List/Cons:
      (a, b) = pairs.head
      if get_at(c, a) == get_at(c, b):
        return collect(c, pairs.tail, insert_sorted(pairs.head, acc))
      else:
        return collect(c, pairs.tail, acc)
