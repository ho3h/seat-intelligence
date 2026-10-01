def prog(x):
  (n, edges) = x
  labels = make_labels(n, 0)
  labels = process_edges(edges, labels)
  return largest(labels, labels, 0)

def make_labels(n, i):
  if i < n:
    return List/Cons(i, make_labels(n, i + 1))
  else:
    return List/Nil

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def rename(xs, old, new):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, rename(xs.tail, old, new))
      else:
        return List/Cons(xs.head, rename(xs.tail, old, new))

def process_edges(edges, labels):
  match edges:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v) = edges.head
      a = get_at(labels, u)
      b = get_at(labels, v)
      if a < b:
        next_labels = rename(labels, b, a)
      else:
        if b < a:
          next_labels = rename(labels, a, b)
        else:
          next_labels = labels
      return process_edges(edges.tail, next_labels)

def count_equal(xs, value, count):
  match xs:
    case List/Nil:
      return count
    case List/Cons:
      if xs.head == value:
        return count_equal(xs.tail, value, count + 1)
      else:
        return count_equal(xs.tail, value, count)

def largest(xs, all_labels, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      size = count_equal(all_labels, xs.head, 0)
      if size > best:
        return largest(xs.tail, all_labels, size)
      else:
        return largest(xs.tail, all_labels, best)
