def prog(x):
  s = sort(x)
  match s:
    case List/Nil:
      return 0
    case List/Cons:
      return scan(s.tail, s.head, 1, 0, 0)

def scan(xs, cur, cnt, best, bcnt):
  match xs:
    case List/Nil:
      if cnt > bcnt:
        return cur
      else:
        return best
    case List/Cons:
      if xs.head == cur:
        return scan(xs.tail, cur, cnt + 1, best, bcnt)
      else:
        if cnt > bcnt:
          return scan(xs.tail, xs.head, 1, cur, cnt)
        else:
          return scan(xs.tail, xs.head, 1, best, bcnt)

def split(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (a, b) = split(xs.tail)
      return (List/Cons(xs.head, b), a)

def merge(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      xh = xs.head
      xt = xs.tail
      match ys:
        case List/Nil:
          return List/Cons(xh, xt)
        case List/Cons:
          yh = ys.head
          yt = ys.tail
          if xh <= yh:
            return List/Cons(xh, merge(xt, List/Cons(yh, yt)))
          else:
            return List/Cons(yh, merge(List/Cons(xh, xt), yt))

def sort(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      h = xs.head
      t = xs.tail
      match t:
        case List/Nil:
          return List/Cons(h, List/Nil)
        case List/Cons:
          (a, b) = split(List/Cons(h, List/Cons(t.head, t.tail)))
          return merge(sort(a), sort(b))
