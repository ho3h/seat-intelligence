def prog(x):
  (n, edges) = x
  labels = make_labels(0, n)
  return process_edges(edges, labels, 0)

def make_labels(i, n):
  if i == n:
    return []
  else:
    rest = make_labels(i + 1, n)
    return List/Cons(i, rest)

def label_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return label_at(xs.tail, i - 1)

def relabel(xs, old_label, new_label):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      tail = relabel(xs.tail, old_label, new_label)
      if xs.head == old_label:
        return List/Cons(new_label, tail)
      else:
        return List/Cons(xs.head, tail)

def process_edges(edges, labels, cycles):
  match edges:
    case List/Nil:
      return cycles
    case List/Cons:
      (u, v) = edges.head
      label_u = label_at(labels, u)
      label_v = label_at(labels, v)
      if label_u == label_v:
        return process_edges(edges.tail, labels, cycles + 1)
      else:
        merged = relabel(labels, label_v, label_u)
        return process_edges(edges.tail, merged, cycles)
