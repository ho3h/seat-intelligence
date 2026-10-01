type Tree: Leaf {value} | Node {left, right}

def prog(x):
  (n, edges) = x
  if n <= 1:
    return 0
  else:
    adj = make_tree(0, n, [])
    adj2 = add_edges(adj, edges, n)
    return sum_sources(adj2, n, 0, n)

def make_tree(lo, hi, value):
  if lo + 1 >= hi:
    return Tree/Leaf(value)
  else:
    mid = (lo + hi) / 2
    left = make_tree(lo, mid, value)
    right = make_tree(mid, hi, value)
    return Tree/Node(left, right)

def tree_get(tree, index, lo, hi):
  match tree:
    case Tree/Leaf:
      return tree.value
    case Tree/Node:
      mid = (lo + hi) / 2
      if index < mid:
        return tree_get(tree.left, index, lo, mid)
      else:
        return tree_get(tree.right, index, mid, hi)

def tree_set(tree, index, value, lo, hi):
  match tree:
    case Tree/Leaf:
      return Tree/Leaf(value)
    case Tree/Node:
      mid = (lo + hi) / 2
      if index < mid:
        left = tree_set(tree.left, index, value, lo, mid)
        return Tree/Node(left, tree.right)
      else:
        right = tree_set(tree.right, index, value, mid, hi)
        return Tree/Node(tree.left, right)

def add_edges(adj, edges, n):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      ns_u = tree_get(adj, u, 0, n)
      ns_v = tree_get(adj, v, 0, n)
      adj1 = tree_set(adj, u, List/Cons(v, ns_u), 0, n)
      adj2 = tree_set(adj1, v, List/Cons(u, ns_v), 0, n)
      return add_edges(adj2, edges.tail, n)

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))

def visit_neighbors(ns, seen, rear, distance, source, total, blocks):
  match ns:
    case List/Nil:
      return (seen, rear, total)
    case List/Cons:
      v = ns.head
      block = v / 24
      bit = 1 << (v % 24)
      old = tree_get(seen, block, 0, blocks)
      if (old & bit) == 0:
        seen2 = tree_set(seen, block, old | bit, 0, blocks)
        rear2 = List/Cons((v, distance + 1), rear)
        if v > source:
          return visit_neighbors(ns.tail, seen2, rear2, distance, source, total + distance + 1, blocks)
        else:
          return visit_neighbors(ns.tail, seen2, rear2, distance, source, total, blocks)
      else:
        return visit_neighbors(ns.tail, seen, rear, distance, source, total, blocks)

def bfs(adj, n, blocks, seen, front, rear, source, total):
  match front:
    case List/Nil:
      match rear:
        case List/Nil:
          return total
        case List/Cons:
          front2 = reverse_acc(rear, [])
          return bfs(adj, n, blocks, seen, front2, [], source, total)
    case List/Cons:
      (u, distance) = front.head
      ns = tree_get(adj, u, 0, n)
      (seen2, rear2, total2) = visit_neighbors(ns, seen, rear, distance, source, total, blocks)
      return bfs(adj, n, blocks, seen2, front.tail, rear2, source, total2)

def source_total(adj, n, source):
  blocks = (n + 23) / 24
  seen = make_tree(0, blocks, 0)
  block = source / 24
  bit = 1 << (source % 24)
  old = tree_get(seen, block, 0, blocks)
  seen2 = tree_set(seen, block, old | bit, 0, blocks)
  return bfs(adj, n, blocks, seen2, List/Cons((source, 0), []), [], source, 0)

def sum_sources(adj, n, lo, hi):
  if lo + 1 >= hi:
    if lo < hi:
      return source_total(adj, n, lo)
    else:
      return 0
  else:
    mid = (lo + hi) / 2
    left = sum_sources(adj, n, lo, mid)
    right = sum_sources(adj, n, mid, hi)
    return left + right
