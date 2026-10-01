def prog(cands):
  return process(cands, List/Nil)

def process(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if u < v:
        acc2 = insert(acc, u, v, score)
        return process(xs.tail, acc2)
      else:
        acc2 = insert(acc, v, u, score)
        return process(xs.tail, acc2)

def insert(xs, u, v, score):
  match xs:
    case List/Nil:
      return List/Cons((u, v, score), List/Nil)
    case List/Cons:
      (a, b, old_score) = xs.head
      if a == u:
        if b == v:
          if score > old_score:
            return List/Cons((a, b, score), xs.tail)
          else:
            return xs
        else:
          if v < b:
            return List/Cons((u, v, score), xs)
          else:
            tail2 = insert(xs.tail, u, v, score)
            return List/Cons(xs.head, tail2)
      else:
        if u < a:
          return List/Cons((u, v, score), xs)
        else:
          tail2 = insert(xs.tail, u, v, score)
          return List/Cons(xs.head, tail2)
