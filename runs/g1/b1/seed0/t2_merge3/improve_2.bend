def prog(x):
  (xs, ys, zs) = x
  return merge3(xs, ys, zs)

def merge3(xs, ys, zs):
  match xs:
    case List/Nil:
      return merge2(ys, zs)
    case List/Cons:
      match ys:
        case List/Nil:
          return merge2(xs, zs)
        case List/Cons:
          match zs:
            case List/Nil:
              return merge2(xs, ys)
            case List/Cons:
              if xs.head <= ys.head:
                if xs.head <= zs.head:
                  return emit3(xs.head, xs, ys, zs)
                else:
                  return emit3(zs.head, xs, ys, zs)
              else:
                if ys.head <= zs.head:
                  return emit3(ys.head, xs, ys, zs)
                else:
                  return emit3(zs.head, xs, ys, zs)

def emit3(v, xs, ys, zs):
  (xs2, nx) = pop_equal(xs, v)
  (ys2, ny) = pop_equal(ys, v)
  (zs2, nz) = pop_equal(zs, v)
  return repeat(v, nx + ny + nz, merge3(xs2, ys2, zs2))

def pop_equal(xs, v):
  match xs:
    case List/Nil:
      return (xs, 0)
    case List/Cons:
      if xs.head == v:
        return (xs.tail, 1)
      else:
        return (xs, 0)

def merge2(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      match ys:
        case List/Nil:
          return xs
        case List/Cons:
          if xs.head < ys.head:
            return List/Cons(xs.head, merge2(xs.tail, ys))
          else:
            if ys.head < xs.head:
              return List/Cons(ys.head, merge2(xs, ys.tail))
            else:
              return repeat(xs.head, 2, merge2(xs.tail, ys.tail))

def repeat(v, n, tail):
  switch n:
    case 0:
      return tail
    case _:
      return List/Cons(v, repeat(v, n - 1, tail))
