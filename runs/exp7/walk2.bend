def prog(x):
  (n, es) = x
  return (len(es), 0)

def len(es):
  match es:
    case List/Nil:
      return 0
    case List/Cons:
      match t = es.tail:
        case List/Nil:
          return 1
        case List/Cons:
          match r = t.tail:
            case List/Nil:
              return 2
            case List/Cons:
              match q = r.tail:
                case List/Nil:
                  return 3
                case List/Cons:
                  return 4 + len(q.tail)
