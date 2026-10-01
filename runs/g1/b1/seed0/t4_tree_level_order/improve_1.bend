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
          return bfs(front.tail, back, out_rev)
        case Gtree/C1:
          back_next = List/Cons(front.head.f2, List/Cons(front.head.f0, back))
          out_next = List/Cons(front.head.f1, out_rev)
          return bfs(front.tail, back_next, out_next)

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
