def prog(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return scan8(xs.tail, 1, 0, xs.head)

def pick(i1, v1, i2, v2):
  if v1 >= v2:
    return (i1, v1)
  else:
    return (i2, v2)

def scan_rest(xs, idx, best_idx, best_val):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      if xs.head > best_val:
        return scan_rest(xs.tail, idx + 1, idx, xs.head)
      else:
        return scan_rest(xs.tail, idx + 1, best_idx, best_val)

def scan8(xs, idx, best_idx, best_val):
  match xs:
    case List/Nil:
      return best_idx
    case List/Cons:
      v0 = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return scan_rest(xs, idx, best_idx, best_val)
        case List/Cons:
          v1 = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return scan_rest(xs, idx, best_idx, best_val)
            case List/Cons:
              v2 = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return scan_rest(xs, idx, best_idx, best_val)
                case List/Cons:
                  v3 = t3.head
                  t4 = t3.tail
                  match t4:
                    case List/Nil:
                      return scan_rest(xs, idx, best_idx, best_val)
                    case List/Cons:
                      v4 = t4.head
                      t5 = t4.tail
                      match t5:
                        case List/Nil:
                          return scan_rest(xs, idx, best_idx, best_val)
                        case List/Cons:
                          v5 = t5.head
                          t6 = t5.tail
                          match t6:
                            case List/Nil:
                              return scan_rest(xs, idx, best_idx, best_val)
                            case List/Cons:
                              v6 = t6.head
                              t7 = t6.tail
                              match t7:
                                case List/Nil:
                                  return scan_rest(xs, idx, best_idx, best_val)
                                case List/Cons:
                                  v7 = t7.head
                                  t8 = t7.tail
                                  (i01, m01) = pick(idx, v0, idx + 1, v1)
                                  (i23, m23) = pick(idx + 2, v2, idx + 3, v3)
                                  (i45, m45) = pick(idx + 4, v4, idx + 5, v5)
                                  (i67, m67) = pick(idx + 6, v6, idx + 7, v7)
                                  (i03, m03) = pick(i01, m01, i23, m23)
                                  (i47, m47) = pick(i45, m45, i67, m67)
                                  (ib, mb) = pick(i03, m03, i47, m47)
                                  (in, vn) = pick(best_idx, best_val, ib, mb)
                                  return scan8(t8, idx + 8, in, vn)
