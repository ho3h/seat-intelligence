def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return argmin_scan(xs, 0, xs.head, 0)

def argmin_pick(a, ai, b, bi):
  if a <= b:
    return (a, ai)
  else:
    return (b, bi)

def argmin_scan(xs, idx, best, best_idx):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      a = xs.head
      ys = xs.tail
      match ys:
        case List/Nil:
          (v, i) = argmin_pick(best, best_idx, a, idx)
          return i
        case List/Cons:
          b = ys.head
          zs = ys.tail
          match zs:
            case List/Nil:
              (v1, i1) = argmin_pick(a, idx, b, idx + 1)
              (v2, i2) = argmin_pick(best, best_idx, v1, i1)
              return i2
            case List/Cons:
              c = zs.head
              ws = zs.tail
              match ws:
                case List/Nil:
                  (v1, i1) = argmin_pick(a, idx, b, idx + 1)
                  (v2, i2) = argmin_pick(v1, i1, c, idx + 2)
                  (v3, i3) = argmin_pick(best, best_idx, v2, i2)
                  return i3
                case List/Cons:
                  d = ws.head
                  (v1, i1) = argmin_pick(a, idx, b, idx + 1)
                  (v2, i2) = argmin_pick(c, idx + 2, d, idx + 3)
                  (v3, i3) = argmin_pick(v1, i1, v2, i2)
                  (v4, i4) = argmin_pick(best, best_idx, v3, i3)
                  return argmin_scan(ws.tail, idx + 4, v4, i4)
