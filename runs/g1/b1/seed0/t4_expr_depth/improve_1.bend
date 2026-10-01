def prog(x):
  return depth2(x)

def depth2(x):
  match x:
    case Gexpr/C0:
      return 1
    case Gexpr/C1:
      a = x.f0
      b = x.f1
      match a:
        case Gexpr/C0:
          match b:
            case Gexpr/C0:
              return 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              return bm + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              return bm + 2
        case Gexpr/C1:
          a0 = depth2(a.f0)
          a1 = depth2(a.f1)
          am = a0 ^ ((a0 ^ a1) & (0 - (a0 < a1)))
          match b:
            case Gexpr/C0:
              return am + 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
        case Gexpr/C2:
          a0 = depth2(a.f0)
          a1 = depth2(a.f1)
          am = a0 ^ ((a0 ^ a1) & (0 - (a0 < a1)))
          match b:
            case Gexpr/C0:
              return am + 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
    case Gexpr/C2:
      a = x.f0
      b = x.f1
      match a:
        case Gexpr/C0:
          match b:
            case Gexpr/C0:
              return 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              return bm + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              return bm + 2
        case Gexpr/C1:
          a0 = depth2(a.f0)
          a1 = depth2(a.f1)
          am = a0 ^ ((a0 ^ a1) & (0 - (a0 < a1)))
          match b:
            case Gexpr/C0:
              return am + 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
        case Gexpr/C2:
          a0 = depth2(a.f0)
          a1 = depth2(a.f1)
          am = a0 ^ ((a0 ^ a1) & (0 - (a0 < a1)))
          match b:
            case Gexpr/C0:
              return am + 2
            case Gexpr/C1:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
            case Gexpr/C2:
              b0 = depth2(b.f0)
              b1 = depth2(b.f1)
              bm = b0 ^ ((b0 ^ b1) & (0 - (b0 < b1)))
              m = am ^ ((am ^ bm) & (0 - (am < bm)))
              return m + 2
