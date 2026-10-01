def prog(x):
  (xs, t) = x
  return lb16(xs, t)

def lb16(xs, t):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head < t:
        a = xs.tail
        match a:
          case List/Nil:
            return 1
          case List/Cons:
            if a.head < t:
              b = a.tail
              match b:
                case List/Nil:
                  return 2
                case List/Cons:
                  if b.head < t:
                    c = b.tail
                    match c:
                      case List/Nil:
                        return 3
                      case List/Cons:
                        if c.head < t:
                          d = c.tail
                          match d:
                            case List/Nil:
                              return 4
                            case List/Cons:
                              if d.head < t:
                                e = d.tail
                                match e:
                                  case List/Nil:
                                    return 5
                                  case List/Cons:
                                    if e.head < t:
                                      f = e.tail
                                      match f:
                                        case List/Nil:
                                          return 6
                                        case List/Cons:
                                          if f.head < t:
                                            g = f.tail
                                            match g:
                                              case List/Nil:
                                                return 7
                                              case List/Cons:
                                                if g.head < t:
                                                  h = g.tail
                                                  match h:
                                                    case List/Nil:
                                                      return 8
                                                    case List/Cons:
                                                      if h.head < t:
                                                        i = h.tail
                                                        match i:
                                                          case List/Nil:
                                                            return 9
                                                          case List/Cons:
                                                            if i.head < t:
                                                              j = i.tail
                                                              match j:
                                                                case List/Nil:
                                                                  return 10
                                                                case List/Cons:
                                                                  if j.head < t:
                                                                    k = j.tail
                                                                    match k:
                                                                      case List/Nil:
                                                                        return 11
                                                                      case List/Cons:
                                                                        if k.head < t:
                                                                          l = k.tail
                                                                          match l:
                                                                            case List/Nil:
                                                                              return 12
                                                                            case List/Cons:
                                                                              if l.head < t:
                                                                                m = l.tail
                                                                                match m:
                                                                                  case List/Nil:
                                                                                    return 13
                                                                                  case List/Cons:
                                                                                    if m.head < t:
                                                                                      n = m.tail
                                                                                      match n:
                                                                                        case List/Nil:
                                                                                          return 14
                                                                                        case List/Cons:
                                                                                          if n.head < t:
                                                                                            o = n.tail
                                                                                            match o:
                                                                                              case List/Nil:
                                                                                                return 15
                                                                                              case List/Cons:
                                                                                                if o.head < t:
                                                                                                  return 16 + lb16(o.tail, t)
                                                                                                else:
                                                                                                  return 15
                                                                                          else:
                                                                                            return 14
                                                                                    else:
                                                                                      return 13
                                                                              else:
                                                                                return 12
                                                                        else:
                                                                          return 11
                                                                  else:
                                                                    return 10
                                                          else:
                                                            return 9
                                                    else:
                                                      return 8
                                              else:
                                                return 7
                                        else:
                                          return 6
                                  else:
                                    return 5
                            else:
                              return 4
                      else:
                        return 3
                  else:
                    return 2
            else:
              return 1
      else:
        return 0
