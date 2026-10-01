def prog(x):
  (n, edges) = x
  if n == 0:
    return ([], [])
  else:
    ins = make_tree(n)
    outs = make_tree(n)
    (ins, outs) = count_edges(edges, n, ins, outs)
    ins_list = collect(ins, n, [])
    outs_list = collect(outs, n, [])
    return (ins_list, outs_list)

def make_tree(n):
  if n == 1:
    return [0]
  else:
    half = n / 2
    left = make_tree(half)
    right = make_tree(n - half)
    return List/Cons(left, List/Cons(right, List/Nil))

def add_at(tree, size, index):
  if size == 1:
    return [tree.head + 1]
  else:
    half = size / 2
    if index < half:
      left = add_at(tree.head, half, index)
      return List/Cons(left, List/Cons(tree.tail.head, List/Nil))
    else:
      right_size = size - half
      right = add_at(tree.tail.head, right_size, index - half)
      return List/Cons(tree.head, List/Cons(right, List/Nil))

def count_edges(edges, n, ins, outs):
  match edges:
    case List/Nil:
      return (ins, outs)
    case List/Cons:
      (u, v) = edges.head
      ins2 = add_at(ins, n, v)
      outs2 = add_at(outs, n, u)
      return count_edges(edges.tail, n, ins2, outs2)

def collect(tree, size, acc):
  if size == 1:
    return List/Cons(tree.head, acc)
  else:
    half = size / 2
    right_acc = collect(tree.tail.head, size - half, acc)
    return collect(tree.head, half, right_acc)
