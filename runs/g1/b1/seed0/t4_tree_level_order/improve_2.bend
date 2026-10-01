def prog(tree):
  return bfs([tree], [], [])

def bfs(front, back, out_rev):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return reverse(out_rev)
        case List/Cons:
          return bfs(reverse(back), [], out_rev)
    case List/Cons:
      match front.head:
        case Gtree/C0:
          match front.tail:
            case List/Nil:
              return bfs([], back, out_rev)
            case List/Cons:
              match front.tail.head:
                case Gtree/C0:
                  return bfs(front.tail.tail, back, out_rev)
                case Gtree/C1:
                  back2 = List/Cons(front.tail.head.f2, List/Cons(front.tail.head.f0, back))
                  out2 = List/Cons(front.tail.head.f1, out_rev)
                  return bfs(front.tail.tail, back2, out2)
        case Gtree/C1:
          back1 = List/Cons(front.head.f2, List/Cons(front.head.f0, back))
          out1 = List/Cons(front.head.f1, out_rev)
          match front.tail:
            case List/Nil:
              return bfs([], back1, out1)
            case List/Cons:
              match front.tail.head:
                case Gtree/C0:
                  return bfs(front.tail.tail, back1, out1)
                case Gtree/C1:
                  back2 = List/Cons(front.tail.head.f2, List/Cons(front.tail.head.f0, back1))
                  out2 = List/Cons(front.tail.head.f1, out1)
                  return bfs(front.tail.tail, back2, out2)

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return List/Cons(xs.head, acc)
        case List/Cons:
          acc_next = List/Cons(xs.tail.head, List/Cons(xs.head, acc))
          return reverse_acc(xs.tail.tail, acc_next)
