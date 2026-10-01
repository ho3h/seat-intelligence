def prog(x):
  (k, key, clusters, attrs) = x
  selected = filter_attrs(attrs, key, [])
  ordered = sort_pairs(selected)
  values = gather_values(clusters, ordered, 0, k, [])
  sorted_values = sort_nums(values)
  return mode(sorted_values)

def filter_attrs(attrs, key, acc):
  match attrs:
    case List/Nil:
      return acc
    case List/Cons:
      (node, attr_key, value) = attrs.head
      if attr_key == key:
        return filter_attrs(attrs.tail, key, List/Cons((node, value), acc))
      else:
        return filter_attrs(attrs.tail, key, acc)

def gather_values(clusters, attrs, node_id, k, acc):
  match clusters:
    case List/Nil:
      return acc
    case List/Cons:
      match attrs:
        case List/Nil:
          return acc
        case List/Cons:
          (attr_node, value) = attrs.head
          if attr_node == node_id:
            if clusters.head == k:
              return gather_values(clusters.tail, attrs.tail, node_id + 1, k, List/Cons(value, acc))
            else:
              return gather_values(clusters.tail, attrs.tail, node_id + 1, k, acc)
          else:
            return gather_values(clusters.tail, attrs, node_id + 1, k, acc)

def split_pairs(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      rest = xs.tail
      match rest:
        case List/Nil:
          return ([xs.head], [])
        case List/Cons:
          (left, right) = split_pairs(rest.tail)
          return (List/Cons(xs.head, left), List/Cons(rest.head, right))

def merge_pairs(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          (a_node, a_value) = a.head
          (b_node, b_value) = b.head
          if a_node <= b_node:
            return List/Cons(a.head, merge_pairs(a.tail, b))
          else:
            return List/Cons(b.head, merge_pairs(a, b.tail))

def sort_pairs(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_pairs(xs)
          return merge_pairs(sort_pairs(left), sort_pairs(right))

def middle_value(slow, fast):
  match fast:
    case List/Nil:
      return slow.head
    case List/Cons:
      match fast.tail:
        case List/Nil:
          return slow.head
        case List/Cons:
          return middle_value(slow.tail, fast.tail.tail)

def partition_nums(xs, pivot, less, equal, greater):
  match xs:
    case List/Nil:
      return (less, equal, greater)
    case List/Cons:
      if xs.head < pivot:
        return partition_nums(xs.tail, pivot, List/Cons(xs.head, less), equal, greater)
      else:
        if xs.head > pivot:
          return partition_nums(xs.tail, pivot, less, equal, List/Cons(xs.head, greater))
        else:
          return partition_nums(xs.tail, pivot, less, List/Cons(xs.head, equal), greater)

def append_nums(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      return List/Cons(a.head, append_nums(a.tail, b))

def sort_nums(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          pivot = middle_value(xs, xs)
          (less, equal, greater) = partition_nums(xs, pivot, [], [], [])
          return append_nums(sort_nums(less), append_nums(equal, sort_nums(greater)))

def mode(xs):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      return mode_scan(xs.tail, xs.head, 1, xs.head, 0)

def mode_scan(xs, current, current_count, best, best_count):
  match xs:
    case List/Nil:
      if current_count > best_count:
        return current
      else:
        return best
    case List/Cons:
      if xs.head == current:
        return mode_scan(xs.tail, current, current_count + 1, best, best_count)
      else:
        if current_count > best_count:
          return mode_scan(xs.tail, xs.head, 1, current, current_count)
        else:
          return mode_scan(xs.tail, xs.head, 1, best, best_count)
