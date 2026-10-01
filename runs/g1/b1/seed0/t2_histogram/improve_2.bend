def prog(xs):
  h = ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
  return histogram(xs, h, h, h, h)

def inc4(v, g):
  (a, b, c, d) = g
  if v == 0:
    return (a + 1, b, c, d)
  else:
    if v == 1:
      return (a, b + 1, c, d)
    else:
      if v == 2:
        return (a, b, c + 1, d)
      else:
        return (a, b, c, d + 1)

def inc16(v, h):
  (g0, g1, g2, g3) = h
  if v < 4:
    return (inc4(v, g0), g1, g2, g3)
  else:
    if v < 8:
      return (g0, inc4(v - 4, g1), g2, g3)
    else:
      if v < 12:
        return (g0, g1, inc4(v - 8, g2), g3)
      else:
        return (g0, g1, g2, inc4(v - 12, g3))

def finish(h0, h1, h2, h3):
  ((a0, a1, a2, a3), (b0, b1, b2, b3), (c0, c1, c2, c3), (d0, d1, d2, d3)) = h0
  ((e0, e1, e2, e3), (f0, f1, f2, f3), (g0, g1, g2, g3), (i0, i1, i2, i3)) = h1
  ((j0, j1, j2, j3), (k0, k1, k2, k3), (l0, l1, l2, l3), (m0, m1, m2, m3)) = h2
  ((n0, n1, n2, n3), (o0, o1, o2, o3), (p0, p1, p2, p3), (q0, q1, q2, q3)) = h3
  return [
    a0 + e0 + j0 + n0, a1 + e1 + j1 + n1, a2 + e2 + j2 + n2, a3 + e3 + j3 + n3,
    b0 + f0 + k0 + o0, b1 + f1 + k1 + o1, b2 + f2 + k2 + o2, b3 + f3 + k3 + o3,
    c0 + g0 + l0 + p0, c1 + g1 + l1 + p1, c2 + g2 + l2 + p2, c3 + g3 + l3 + p3,
    d0 + i0 + m0 + q0, d1 + i1 + m1 + q1, d2 + i2 + m2 + q2, d3 + i3 + m3 + q3
  ]

def histogram(xs, h0, h1, h2, h3):
  match xs:
    case List/Nil:
      return finish(h0, h1, h2, h3)
    case List/Cons:
      x0 = xs.head
      match xs.tail:
        case List/Nil:
          return finish(inc16(x0, h0), h1, h2, h3)
        case List/Cons:
          x1 = xs.tail.head
          match xs.tail.tail:
            case List/Nil:
              return finish(inc16(x0, h0), inc16(x1, h1), h2, h3)
            case List/Cons:
              x2 = xs.tail.tail.head
              match xs.tail.tail.tail:
                case List/Nil:
                  return finish(inc16(x0, h0), inc16(x1, h1), inc16(x2, h2), h3)
                case List/Cons:
                  x3 = xs.tail.tail.tail.head
                  return histogram(
                    xs.tail.tail.tail.tail,
                    inc16(x0, h0),
                    inc16(x1, h1),
                    inc16(x2, h2),
                    inc16(x3, h3)
                  )
