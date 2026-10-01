def prog(xs):
  tails = build_tails(xs, [])
  return list_length(tails)

def build_tails(xs, tails):
  match xs:
    case List/Nil:
      return tails
    case List/Cons:
      next_tails = insert_or_replace(tails, xs.head)
      return build_tails(xs.tail, next_tails)

def insert_or_replace(tails, value):
  match tails:
    case List/Nil:
      return [value]
    case List/Cons:
      if tails.head >= value:
        return List/Cons(value, tails.tail)
      else:
        return List/Cons(tails.head, insert_or_replace(tails.tail, value))

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)
