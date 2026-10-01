def prog(tree):
  return bfs([tree], [])

def bfs(frontier, out_rev):
  match frontier:
    case List/Nil:
      return reverse(out_rev)
    case List/Cons:
      (out_next, next_rev) = process_level(frontier, out_rev, [])
      return bfs(reverse(next_rev), out_next)

def process_level(nodes, out_rev, next_rev):
  match nodes:
    case List/Nil:
      return (out_rev, next_rev)
    case List/Cons:
      match nodes.head:
        case Gtree/C0:
          return process_level(nodes.tail, out_rev, next_rev)
        case Gtree/C1:
          out_next = List/Cons(nodes.head.f1, out_rev)
          next_left = List/Cons(nodes.head.f0, next_rev)
          next_both = List/Cons(nodes.head.f2, next_left)
          return process_level(nodes.tail, out_next, next_both)

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
